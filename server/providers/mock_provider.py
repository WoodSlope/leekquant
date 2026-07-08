from __future__ import annotations

from copy import deepcopy


TODAY_MARKET = {
    "date": "2026-05-20",
    "indexAboveMa": True,
    "limitDownCount": 12,
    "crashDays": 0,
    "marketDrop": 1.25,
    "marketVolRatio": 1.62,
    "ma20Up": True,
    "time": "14:05",
    "stocks": [
        {
            "id": "600519",
            "name": "贵州茅台",
            "closeAbovePrev": True,
            "closeAboveOpen": True,
            "highDays": 22,
            "platformDays": 24,
            "platformAmp": 8.6,
            "gapUp": False,
            "pullbackDays": 4,
            "lowerShadowRatio": 1.3,
            "surgePct": 2.8,
            "aboveMa": True,
            "fundSafeDays": 7,
            "macdCross": True,
            "superInflowDays": 2,
            "volRatio": 2.1,
            "rsi": 43,
            "mainInflowPct": 12.4,
            "northDays": 8,
            "northPct": 0.18,
            "backtestReturn": 16.3,
            "maxLoss": -5.2,
            "exitReason": "移动止盈",
        },
        {
            "id": "000001",
            "name": "平安银行",
            "closeAbovePrev": True,
            "closeAboveOpen": True,
            "highDays": 16,
            "platformDays": 18,
            "platformAmp": 9.8,
            "gapUp": True,
            "pullbackDays": 5,
            "lowerShadowRatio": 2.2,
            "surgePct": 5.4,
            "aboveMa": True,
            "fundSafeDays": 6,
            "macdCross": False,
            "superInflowDays": 1,
            "volRatio": 2.4,
            "rsi": 36,
            "mainInflowPct": 9.6,
            "northDays": 5,
            "northPct": 0.12,
            "backtestReturn": 8.7,
            "maxLoss": -4.1,
            "exitReason": "策略止盈",
        },
        {
            "id": "300750",
            "name": "宁德时代",
            "closeAbovePrev": True,
            "closeAboveOpen": False,
            "highDays": 28,
            "platformDays": 26,
            "platformAmp": 7.4,
            "gapUp": True,
            "pullbackDays": 6,
            "lowerShadowRatio": 1.7,
            "surgePct": 6.1,
            "aboveMa": True,
            "fundSafeDays": 4,
            "macdCross": True,
            "superInflowDays": 2,
            "volRatio": 2.8,
            "rsi": 57,
            "mainInflowPct": 13.1,
            "northDays": 7,
            "northPct": 0.22,
            "backtestReturn": 12.2,
            "maxLoss": -6.5,
            "exitReason": "趋势跟随止盈",
        },
    ],
}


HISTORICAL_MARKETS = [
    {
        "date": "2025-03-01",
        "indexAboveMa": True,
        "limitDownCount": 9,
        "crashDays": 0,
        "marketDrop": 1.4,
        "marketVolRatio": 1.8,
        "ma20Up": True,
        "time": "14:10",
        "stocks": [
            {
                "id": "002594",
                "name": "比亚迪",
                "closeAbovePrev": True,
                "closeAboveOpen": True,
                "highDays": 30,
                "platformDays": 22,
                "platformAmp": 6.6,
                "gapUp": True,
                "pullbackDays": 5,
                "lowerShadowRatio": 1.9,
                "surgePct": 5.8,
                "aboveMa": True,
                "fundSafeDays": 8,
                "macdCross": True,
                "superInflowDays": 2,
                "volRatio": 2.6,
                "rsi": 54,
                "mainInflowPct": 14.2,
                "northDays": 6,
                "northPct": 0.2,
                "backtestReturn": 16.3,
                "maxLoss": -5.1,
                "exitReason": "移动止盈",
            },
            {
                "id": "600036",
                "name": "招商银行",
                "closeAbovePrev": False,
                "closeAboveOpen": False,
                "highDays": 10,
                "platformDays": 15,
                "platformAmp": 12.5,
                "gapUp": False,
                "pullbackDays": 2,
                "lowerShadowRatio": 0.7,
                "surgePct": -0.6,
                "aboveMa": False,
                "fundSafeDays": 2,
                "macdCross": False,
                "superInflowDays": 0,
                "volRatio": 1.1,
                "rsi": 31,
                "mainInflowPct": 3.8,
                "northDays": 2,
                "northPct": 0.04,
                "backtestReturn": -7.9,
                "maxLoss": -8.8,
                "exitReason": "硬止损",
            },
        ],
    },
    {
        "date": "2025-10-08",
        "indexAboveMa": True,
        "limitDownCount": 6,
        "crashDays": 0,
        "marketDrop": 1.1,
        "marketVolRatio": 1.55,
        "ma20Up": True,
        "time": "14:20",
        "stocks": [
            {
                "id": "300750",
                "name": "宁德时代",
                "closeAbovePrev": True,
                "closeAboveOpen": True,
                "highDays": 26,
                "platformDays": 24,
                "platformAmp": 7.1,
                "gapUp": True,
                "pullbackDays": 6,
                "lowerShadowRatio": 1.8,
                "surgePct": 6.5,
                "aboveMa": True,
                "fundSafeDays": 6,
                "macdCross": True,
                "superInflowDays": 2,
                "volRatio": 2.9,
                "rsi": 45,
                "mainInflowPct": 15.8,
                "northDays": 7,
                "northPct": 0.24,
                "backtestReturn": 14.8,
                "maxLoss": -5.9,
                "exitReason": "移动止盈",
            }
        ],
    },
]


class MockProvider:
    name = "mock"

    def today_market(self) -> dict:
        return deepcopy(TODAY_MARKET)

    def historical_markets(self, start: str | None = None, end: str | None = None) -> list[dict]:
        return deepcopy(HISTORICAL_MARKETS)

    def stock_daily(self, code: str, start: str, end: str) -> list[dict]:
        base = 20 + (sum(ord(ch) for ch in code) % 80)
        dates = ["2025-01-02", "2025-01-03", "2025-01-06", "2025-01-07", "2025-01-08"]
        rows = []
        for idx, date in enumerate(dates):
            close = round(base * (1 + idx * 0.012), 2)
            rows.append(
                {
                    "code": code,
                    "date": date,
                    "open": round(close * 0.99, 2),
                    "high": round(close * 1.03, 2),
                    "low": round(close * 0.97, 2),
                    "close": close,
                    "volume": 1000000 + idx * 100000,
                    "amount": close * (1000000 + idx * 100000),
                }
            )
        return [row for row in rows if start <= row["date"].replace("-", "") <= end]
