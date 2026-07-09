from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "cache.sqlite"


class CacheStore:
    def __init__(self, path: Path = DB_PATH):
        DATA_DIR.mkdir(exist_ok=True)
        self.path = path
        self.init_db()

    def connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS market_snapshot (
                    trade_date TEXT PRIMARY KEY,
                    provider TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    fetched_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS stock_daily (
                    code TEXT NOT NULL,
                    trade_date TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume REAL,
                    amount REAL,
                    payload TEXT NOT NULL,
                    fetched_at TEXT NOT NULL,
                    PRIMARY KEY (code, trade_date)
                );

                CREATE TABLE IF NOT EXISTS cache_meta (
                    cache_key TEXT PRIMARY KEY,
                    provider TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    payload TEXT
                );
                """
            )

    def get_market_snapshot_record(self, trade_date: str | None = None, ttl_minutes: int = 5) -> dict | None:
        with self.connect() as conn:
            if trade_date:
                row = conn.execute("SELECT * FROM market_snapshot WHERE trade_date = ?", (trade_date,)).fetchone()
            else:
                row = conn.execute("SELECT * FROM market_snapshot ORDER BY trade_date DESC LIMIT 1").fetchone()
        if not row:
            return None
        if not trade_date and self.is_expired(row["fetched_at"], ttl_minutes):
            return None
        return {
            "tradeDate": row["trade_date"],
            "provider": row["provider"],
            "market": json.loads(row["payload"]),
            "fetchedAt": row["fetched_at"],
        }

    def get_market_snapshot(self, trade_date: str | None = None, ttl_minutes: int = 5) -> dict | None:
        record = self.get_market_snapshot_record(trade_date=trade_date, ttl_minutes=ttl_minutes)
        return record["market"] if record else None

    def save_market_snapshot(self, market: dict, provider: str):
        trade_date = market.get("date") or datetime.now().strftime("%Y-%m-%d")
        with self.connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO market_snapshot (trade_date, provider, payload, fetched_at)
                VALUES (?, ?, ?, ?)
                """,
                (trade_date, provider, json.dumps(market, ensure_ascii=False), self.now()),
            )

    def get_daily_range(self, code: str, start: str, end: str) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT payload FROM stock_daily
                WHERE code = ? AND trade_date >= ? AND trade_date <= ?
                ORDER BY trade_date
                """,
                (code, start, end),
            ).fetchall()
        return [json.loads(row["payload"]) for row in rows]

    def get_daily_bounds(self, code: str) -> tuple[str | None, str | None]:
        with self.connect() as conn:
            row = conn.execute("SELECT MIN(trade_date) AS min_date, MAX(trade_date) AS max_date FROM stock_daily WHERE code = ?", (code,)).fetchone()
        return row["min_date"], row["max_date"]

    def save_daily(self, code: str, rows: list[dict], provider: str):
        if not rows:
            return
        with self.connect() as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO stock_daily
                (code, trade_date, provider, open, high, low, close, volume, amount, payload, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        code,
                        row.get("date"),
                        provider,
                        row.get("open"),
                        row.get("high"),
                        row.get("low"),
                        row.get("close"),
                        row.get("volume"),
                        row.get("amount"),
                        json.dumps(row, ensure_ascii=False),
                        self.now(),
                    )
                    for row in rows
                    if row.get("date")
                ],
            )

    def cache_info(self) -> dict:
        with self.connect() as conn:
            snapshot_count = conn.execute("SELECT COUNT(*) AS c FROM market_snapshot").fetchone()["c"]
            daily_count = conn.execute("SELECT COUNT(*) AS c FROM stock_daily").fetchone()["c"]
            code_count = conn.execute("SELECT COUNT(DISTINCT code) AS c FROM stock_daily").fetchone()["c"]
        return {
            "path": str(self.path),
            "marketSnapshots": snapshot_count,
            "dailyRows": daily_count,
            "stockCodes": code_count,
        }

    @staticmethod
    def is_expired(fetched_at: str, ttl_minutes: int) -> bool:
        try:
            fetched = datetime.fromisoformat(fetched_at)
        except ValueError:
            return True
        return datetime.now() - fetched > timedelta(minutes=ttl_minutes)

    @staticmethod
    def now() -> str:
        return datetime.now().isoformat(timespec="seconds")
