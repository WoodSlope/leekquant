from __future__ import annotations

import types
import unittest
from unittest.mock import patch

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


if __name__ == "__main__":
    unittest.main()
