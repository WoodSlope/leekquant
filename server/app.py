from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from server.engine.rules import backtest, scan  # noqa: E402
from server.providers.mock_provider import MockProvider  # noqa: E402
from server.storage import CacheStore  # noqa: E402


STORE = CacheStore()


def get_provider():
    warnings: list[str] = []
    try:
        from server.providers.akshare_provider import AkshareProvider

        return AkshareProvider(), warnings
    except Exception as exc:
        warnings.append(str(exc))
        return MockProvider(), warnings


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            provider, warnings = get_provider()
            return self.json({"ok": True, "provider": provider.name, "warnings": warnings, "cache": STORE.cache_info()})
        if parsed.path == "/api/a/market/snapshot":
            return self.handle_market_snapshot()
        if parsed.path.startswith("/api/a/stocks/") and parsed.path.endswith("/daily"):
            return self.handle_stock_daily(parsed)
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/a/scan":
            return self.handle_scan()
        if parsed.path == "/api/a/backtest":
            return self.handle_backtest()
        self.send_error(404, "Not Found")

    def handle_market_snapshot(self):
        provider, warnings = get_provider()
        cached = STORE.get_market_snapshot(ttl_minutes=5)
        if cached:
            return self.json({"ok": True, "provider": "cache", "warnings": warnings, "market": cached, "cache": STORE.cache_info()})
        try:
            market = provider.today_market()
            STORE.save_market_snapshot(market, provider.name)
            return self.json({"ok": True, "provider": provider.name, "warnings": warnings, "market": market, "cache": STORE.cache_info()})
        except Exception as exc:
            fallback = MockProvider()
            warnings.append(str(exc))
            market = fallback.today_market()
            STORE.save_market_snapshot(market, fallback.name)
            return self.json({"ok": True, "provider": fallback.name, "warnings": warnings, "market": market, "cache": STORE.cache_info()})

    def handle_scan(self):
        payload = self.read_json()
        provider, warnings = get_provider()
        try:
            market = STORE.get_market_snapshot(ttl_minutes=5) or provider.today_market()
            STORE.save_market_snapshot(market, provider.name)
        except Exception as exc:
            fallback = MockProvider()
            warnings.append(str(exc))
            provider = fallback
            market = fallback.today_market()
            STORE.save_market_snapshot(market, fallback.name)
        result = scan(
            payload.get("config") or {},
            market,
            executed_ids=payload.get("executedSignalIds") or [],
            position_ids=payload.get("positionIds") or [],
        )
        return self.json({"ok": True, "provider": provider.name, "warnings": warnings, **result})

    def handle_backtest(self):
        payload = self.read_json()
        query = parse_qs(urlparse(self.path).query)
        provider, warnings = get_provider()
        start = payload.get("start") or query.get("start", [None])[0]
        end = payload.get("end") or query.get("end", [None])[0]
        try:
            markets = provider.historical_markets(start=start, end=end)
        except Exception as exc:
            fallback = MockProvider()
            warnings.append(str(exc))
            provider = fallback
            markets = fallback.historical_markets(start=start, end=end)
        result = backtest(payload.get("config") or {}, markets, payload.get("name") or "未命名回测", payload.get("range") or f"{start or ''} ~ {end or ''}")
        return self.json({"ok": True, "provider": provider.name, "warnings": warnings, "backtest": result})

    def handle_stock_daily(self, parsed):
        parts = parsed.path.strip("/").split("/")
        code = parts[3] if len(parts) >= 5 else ""
        query = parse_qs(parsed.query)
        start = query.get("start", ["20200101"])[0]
        end = query.get("end", ["20991231"])[0]
        provider, warnings = get_provider()

        cached_rows = STORE.get_daily_range(code, self.date_key(start), self.date_key(end))
        _, max_date = STORE.get_daily_bounds(code)
        fetch_start = start
        if max_date:
            next_day = (datetime.strptime(max_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y%m%d")
            if next_day >= start:
                fetch_start = next_day

        fetched_rows = []
        try:
            fetched_rows = provider.stock_daily(code, fetch_start, end)
            STORE.save_daily(code, fetched_rows, provider.name)
        except Exception as exc:
            warnings.append(str(exc))
            fallback = MockProvider()
            provider = fallback
            fetched_rows = fallback.stock_daily(code, fetch_start, end)
            STORE.save_daily(code, fetched_rows, fallback.name)

        rows = STORE.get_daily_range(code, self.date_key(start), self.date_key(end))
        return self.json({
            "ok": True,
            "provider": provider.name,
            "warnings": warnings,
            "code": code,
            "start": start,
            "end": end,
            "cacheHitRows": len(cached_rows),
            "fetchedRows": len(fetched_rows),
            "rows": rows,
            "cache": STORE.cache_info(),
        })

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0") or "0")
        if not length:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    def json(self, data: dict, status: int = 200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    @staticmethod
    def date_key(value: str) -> str:
        value = value or ""
        if len(value) == 8 and value.isdigit():
            return f"{value[:4]}-{value[4:6]}-{value[6:]}"
        return value


def main():
    port = 8765
    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"LeekQuant server: http://127.0.0.1:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
