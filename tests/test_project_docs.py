from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ProjectDocsTest(unittest.TestCase):
    def test_backtest_task_pool_exists_with_prioritized_items(self):
        path = ROOT / "BACKTEST_TASKS.md"

        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        self.assertIn("严格回测任务池", text)
        self.assertIn("P0", text)
        self.assertIn("逐日扫描", text)
        self.assertIn("持仓", text)
        self.assertIn("离场", text)
        self.assertIn("收益统计", text)


if __name__ == "__main__":
    unittest.main()
