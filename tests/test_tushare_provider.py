from __future__ import annotations

import types
import unittest
from unittest.mock import patch

from server.providers.tushare_provider import TushareProvider


class FakeFrame:
    empty = False

    def __init__(self, rows):
        self.rows = rows

    def to_dict(self, orient):
        self.assert_orient = orient
        return self.rows


class FakePro:
    def daily(self, **kwargs):
        return FakeFrame(
            [
                {
                    "ts_code": "600000.SH",
                    "trade_date": "20260709",
                    "open": 10.1,
                    "high": 10.8,
                    "low": 9.9,
                    "close": 10.5,
                    "vol": 120000,
                    "amount": 1300000,
                    "pct_chg": 2.3,
                }
            ]
        )


class TushareProviderTest(unittest.TestCase):
    def test_requires_token_from_environment_or_dotenv(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "TUSHARE_TOKEN"):
                TushareProvider()

    def test_stock_daily_maps_tushare_rows_to_project_daily_contract(self):
        fake_ts = types.SimpleNamespace(pro_api=lambda token: FakePro())

        with patch.dict("os.environ", {"TUSHARE_TOKEN": "secret"}), patch.dict("sys.modules", {"tushare": fake_ts}):
            provider = TushareProvider()
            rows = provider.stock_daily("600000", "20260701", "20260709")

        self.assertEqual(rows[0]["code"], "600000")
        self.assertEqual(rows[0]["date"], "2026-07-09")
        self.assertEqual(rows[0]["open"], 10.1)
        self.assertEqual(rows[0]["close"], 10.5)
        self.assertEqual(rows[0]["volume"], 120000.0)
        self.assertEqual(rows[0]["amount"], 1300000.0)
        self.assertEqual(rows[0]["pct"], 2.3)


if __name__ == "__main__":
    unittest.main()
