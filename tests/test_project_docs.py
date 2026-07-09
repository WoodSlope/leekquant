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

    def test_readme_documents_one_click_local_start(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

        self.assertIn("双击 `双击启动.command`", readme)
        self.assertIn("bash start.sh", readme)
        self.assertIn("http://127.0.0.1:8765/index.html", readme)
        self.assertNotIn("未包含本地双击启动脚本", readme)
        self.assertNotIn("start.sh", gitignore)
        self.assertNotIn("双击启动.command", gitignore)

    def test_readme_documents_configurable_data_sources(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        env_example = (ROOT / ".env.example").read_text(encoding="utf-8")
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

        self.assertIn("AKShare -> 新浪备用免费源 -> BaoStock -> mock", readme)
        self.assertIn("LEEK_PROVIDER_ORDER", readme)
        self.assertIn("TUSHARE_TOKEN", readme)
        self.assertIn(".env.example", readme)
        self.assertIn("浏览器不会保存 token", readme)
        self.assertIn("Tushare token", readme)
        self.assertIn("TUSHARE_TOKEN=", env_example)
        self.assertIn(".env", gitignore)


if __name__ == "__main__":
    unittest.main()
