from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from server.engine.rules import scan  # noqa: E402
from server.providers.mock_provider import MockProvider  # noqa: E402


DEFAULT_CONFIG_PATH = ROOT / "config" / "default-strategy.json"
DEFAULT_OUTPUT_DIR = ROOT / "public-data"
MODE = "close-scan"


def load_strategy(path: Path = DEFAULT_CONFIG_PATH) -> tuple[str, str, dict]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if "config" in raw:
        return raw.get("name") or "默认收盘策略", raw.get("description") or "", raw["config"]
    return raw.get("name") or "默认收盘策略", raw.get("description") or "", raw


def build_provider(provider_name: str = "auto"):
    warnings: list[str] = []
    if provider_name == "mock":
        return MockProvider(), warnings
    if provider_name not in {"auto", "akshare"}:
        warnings.append(f"未知数据源 {provider_name}，已降级到样本数据")
        return MockProvider(), warnings
    try:
        from server.providers.akshare_provider import AkshareProvider

        return AkshareProvider(), warnings
    except Exception as exc:
        if provider_name == "akshare":
            warnings.append(f"AKShare 初始化失败，已降级到样本数据: {exc}")
        else:
            warnings.append(f"免费行情源不可用，已降级到样本数据: {exc}")
        return MockProvider(), warnings


def get_market(provider, warnings: list[str]) -> tuple[object, dict]:
    try:
        return provider, provider.today_market()
    except Exception as exc:
        warnings.append(f"{provider.name} 行情获取失败，已降级到样本数据: {exc}")
        fallback = MockProvider()
        return fallback, fallback.today_market()


def market_summary(market: dict) -> dict:
    return {
        "date": market.get("date"),
        "time": market.get("time"),
        "indexAboveMa": market.get("indexAboveMa"),
        "limitDownCount": market.get("limitDownCount"),
        "crashDays": market.get("crashDays"),
        "marketDrop": market.get("marketDrop"),
        "marketVolRatio": market.get("marketVolRatio"),
        "ma20Up": market.get("ma20Up"),
        "stockCount": len(market.get("stocks") or []),
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def generate_public_data(
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    config_path: str | Path = DEFAULT_CONFIG_PATH,
    provider_name: str = "auto",
    now: datetime | None = None,
) -> dict:
    output_dir = Path(output_dir)
    config_path = Path(config_path)
    run_at_dt = now or datetime.now(ZoneInfo("Asia/Shanghai"))
    run_at = run_at_dt.strftime("%Y-%m-%d %H:%M:%S")

    strategy_name, strategy_description, config = load_strategy(config_path)
    provider, warnings = build_provider(provider_name)
    provider, market = get_market(provider, warnings)
    result = scan(config, market, executed_ids=[], position_ids=[])
    trade_date = str(result.get("providerDate") or market.get("date") or run_at_dt.strftime("%Y-%m-%d"))

    latest_payload = {
        "ok": True,
        "mode": MODE,
        "runAt": run_at,
        "tradeDate": trade_date,
        "provider": provider.name,
        "strategyName": strategy_name,
        "strategyDescription": strategy_description,
        "warnings": warnings,
        "market": market_summary(market),
        "funnel": result["funnel"],
        "details": result["details"],
        "signals": result["signals"],
    }
    market_payload = {
        "ok": True,
        "mode": MODE,
        "runAt": run_at,
        "tradeDate": trade_date,
        "provider": provider.name,
        "warnings": warnings,
        "market": market,
    }
    status_payload = {
        "ok": True,
        "mode": MODE,
        "runAt": run_at,
        "tradeDate": trade_date,
        "provider": provider.name,
        "warnings": warnings,
        "latestFile": "public-data/latest-scan.json",
        "marketFile": "public-data/market-snapshot.json",
        "historyFile": f"public-data/history/{trade_date}.json",
    }

    write_json(output_dir / "latest-scan.json", latest_payload)
    write_json(output_dir / "market-snapshot.json", market_payload)
    write_json(output_dir / "run-status.json", status_payload)
    write_json(output_dir / "history" / f"{trade_date}.json", latest_payload)

    return status_payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成 GitHub Pages 可读取的收盘扫描静态数据")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="静态 JSON 输出目录")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="策略配置 JSON")
    parser.add_argument("--provider", default="auto", choices=["auto", "akshare", "mock"], help="数据源")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = generate_public_data(output_dir=args.output_dir, config_path=args.config, provider_name=args.provider)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
