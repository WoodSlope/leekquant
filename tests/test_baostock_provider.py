from __future__ import annotations

import types
import unittest
from unittest.mock import patch

from server.engine.rules import scan
from server.providers.baostock_provider import BaostockProvider


class FakeResult:
    def __init__(self, fields, rows):
        self.error_code = "0"
        self.error_msg = ""
        self.fields = fields
        self.rows = rows
        self.index = -1

    def next(self):
        self.index += 1
        return self.index < len(self.rows)

    def get_row_data(self):
        return self.rows[self.index]


class BaostockProviderTest(unittest.TestCase):
    def test_today_market_rejects_empty_current_trade_day(self):
        fake_bs = types.SimpleNamespace()
        fake_bs.login = lambda: types.SimpleNamespace(error_code="0", error_msg="")
        fake_bs.logout = lambda: None
        fake_bs.query_all_stock = lambda day: FakeResult(["code", "code_name"], [])
        fake_bs.query_history_k_data_plus = lambda *args, **kwargs: FakeResult(
            ["date", "close", "volume", "pctChg"],
            [["2026-07-10", "3500", "1000000", "0.5"]],
        )

        with patch.dict("sys.modules", {"baostock": fake_bs}):
            provider = BaostockProvider(limit=1)
            with self.assertRaisesRegex(RuntimeError, "未返回当前交易日股票清单"):
                provider.today_market()

    def test_stock_daily_maps_baostock_rows_to_project_daily_contract(self):
        fake_bs = types.SimpleNamespace()
        fake_bs.login = lambda: types.SimpleNamespace(error_code="0", error_msg="")
        fake_bs.logout = lambda: None
        fake_bs.query_history_k_data_plus = lambda *args, **kwargs: FakeResult(
            ["date", "code", "open", "high", "low", "close", "volume", "amount", "pctChg"],
            [["2026-07-09", "sh.600000", "10.1", "10.8", "9.9", "10.5", "120000", "1300000", "2.3"]],
        )

        with patch.dict("sys.modules", {"baostock": fake_bs}):
            provider = BaostockProvider()
            rows = provider.stock_daily("600000", "20260701", "20260709")

        self.assertEqual(rows[0]["code"], "600000")
        self.assertEqual(rows[0]["date"], "2026-07-09")
        self.assertEqual(rows[0]["open"], 10.1)
        self.assertEqual(rows[0]["close"], 10.5)
        self.assertEqual(rows[0]["amount"], 1300000.0)
        self.assertEqual(rows[0]["pct"], 2.3)

    def test_today_market_outputs_strategy_scan_contract(self):
        fake_bs = types.SimpleNamespace()
        fake_bs.login = lambda: types.SimpleNamespace(error_code="0", error_msg="")
        fake_bs.logout = lambda: None
        fake_bs.query_all_stock = lambda day: FakeResult(
            ["code", "code_name"],
            [["sh.600000", "浦发银行"]],
        )

        def query_history_k_data_plus(code, fields, **kwargs):
            if code == "sh.000001":
                rows = [
                    [f"2026-06-{day:02d}", "3200", "1000000", "0.5"]
                    for day in range(1, 31)
                ]
                return FakeResult(["date", "close", "volume", "pctChg"], rows)
            return FakeResult(
                ["date", "code", "open", "high", "low", "close", "volume", "amount", "pctChg"],
                [["2026-07-09", "sh.600000", "10.0", "10.8", "9.9", "10.5", "120000", "1300000000", "2.3"]],
            )

        fake_bs.query_history_k_data_plus = query_history_k_data_plus

        with patch.dict("sys.modules", {"baostock": fake_bs}):
            provider = BaostockProvider(limit=1)
            market = provider.today_market()

        required_market_fields = {
            "date",
            "indexAboveMa",
            "limitDownCount",
            "crashDays",
            "marketDrop",
            "marketVolRatio",
            "ma20Up",
            "time",
            "stocks",
        }
        required_stock_fields = {
            "id",
            "name",
            "closeAbovePrev",
            "closeAboveOpen",
            "highDays",
            "gapUp",
            "surgePct",
            "aboveMa",
            "fundSafeDays",
            "macdCross",
            "superInflowDays",
            "volRatio",
            "rsi",
            "mainInflowPct",
            "northDays",
            "northPct",
            "backtestReturn",
            "maxLoss",
            "exitReason",
        }

        self.assertTrue(required_market_fields.issubset(market))
        self.assertEqual(len(market["stocks"]), 1)
        self.assertTrue(required_stock_fields.issubset(market["stocks"][0]))
        self.assertEqual(market["stocks"][0]["id"], "600000")
        result = scan({}, market)
        self.assertIn("funnel", result)
        self.assertIn("signals", result)


if __name__ == "__main__":
    unittest.main()
