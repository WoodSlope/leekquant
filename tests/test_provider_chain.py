from __future__ import annotations

import sys
import types
import unittest
from unittest.mock import patch

from server.providers.chain import build_providers, call_provider_method


class ProviderChainTest(unittest.TestCase):
    def test_auto_provider_chain_keeps_sina_before_mock_when_akshare_fails_to_initialize(self):
        class FailingAkshareProvider:
            def __init__(self):
                raise RuntimeError("ak init down")

        class SinaProvider:
            name = "sina"

        fake_sina_module = types.ModuleType("server.providers.sina_provider")
        fake_sina_module.SinaProvider = SinaProvider

        with patch("server.providers.akshare_provider.AkshareProvider", FailingAkshareProvider), patch.dict(
            sys.modules, {"server.providers.sina_provider": fake_sina_module}
        ):
            providers, warnings = build_providers("auto")

        self.assertEqual([provider.name for provider in providers], ["sina", "mock"])
        self.assertTrue(any("AKShare 初始化失败" in item for item in warnings))

    def test_call_provider_method_uses_next_real_provider_before_mock(self):
        class FailingProvider:
            name = "akshare"

            def today_market(self):
                raise RuntimeError("ak market down")

        class SinaProvider:
            name = "sina"

            def today_market(self):
                return {"date": "2026-07-08", "stocks": []}

        warnings: list[str] = []

        provider, market = call_provider_method(
            [FailingProvider(), SinaProvider()],
            warnings,
            "today_market",
            action_label="行情获取",
        )

        self.assertEqual(provider.name, "sina")
        self.assertEqual(market["date"], "2026-07-08")
        self.assertTrue(any("akshare 行情获取失败，已尝试备用免费源" in item for item in warnings))
        self.assertFalse(any("样本数据" in item for item in warnings))


if __name__ == "__main__":
    unittest.main()
