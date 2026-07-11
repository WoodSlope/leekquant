from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from server.storage import CacheStore


class StorageCacheTest(unittest.TestCase):
    def test_market_snapshot_record_preserves_provider_warnings(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = CacheStore(Path(tmp) / "cache.sqlite")
            market = {"date": "2026-07-08", "stocks": []}
            warnings = ["akshare 行情获取失败，已尝试备用免费源"]

            store.save_market_snapshot(market, "sina", warnings=warnings)

            record = store.get_market_snapshot_record(ttl_minutes=5)

            self.assertEqual(record["market"], market)
            self.assertEqual(record["warnings"], warnings)

    def test_market_snapshot_record_keeps_provider_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = CacheStore(Path(tmp) / "cache.sqlite")
            market = {"date": "2026-07-08", "stocks": []}

            store.save_market_snapshot(market, "sina")

            record = store.get_market_snapshot_record(ttl_minutes=5)

            self.assertIsNotNone(record)
            self.assertEqual(record["provider"], "sina")
            self.assertEqual(record["market"], market)
            self.assertEqual(store.get_market_snapshot(ttl_minutes=5), market)


if __name__ == "__main__":
    unittest.main()
