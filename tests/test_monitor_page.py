from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class MonitorPageTest(unittest.TestCase):
    def test_monitor_header_has_manual_scan_button(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn("const handleRunScan = (", html)
        self.assertIn("onClick={handleRunScan}", html)
        self.assertIn("执行扫描", html)
        self.assertIn("bg-blue-600 hover:bg-blue-500 text-white px-3 md:px-4 py-1.5 rounded-md flex items-center text-sm font-medium transition-colors", html)

    def test_monitor_header_omits_context_eyebrow(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")

        title_index = html.index("策略监控台")
        header_start = html.rfind("<PageHeader", 0, title_index)
        monitor_header = html[header_start : html.index("stats={", title_index)]
        self.assertNotIn("eyebrow=", monitor_header)
        self.assertNotIn("本地策略原型", monitor_header)

    def test_monitor_date_picker_is_in_funnel_card_actions(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")

        self.assertGreater(html.index("观测日期"), html.index("策略漏斗总览"))
        self.assertIn("title={<><Icons.Activity className=\"mr-2 text-zinc-400\" size={16}/>策略漏斗总览</>}", html)
        self.assertIn("actions={", html[html.index("策略漏斗总览") : html.index("第 0 步：市场环境")])

    def test_monitor_date_picker_uses_compact_labels(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn('label: "2026-05-20", title: "本地演示"', html)
        self.assertIn('label: "2026-05-19", title: "历史复盘"', html)
        self.assertIn('w-[104px]', html)
        self.assertIn(">日期</span>", html)
        self.assertNotIn('label: "2026-05-20 本地演示"', html)
        self.assertNotIn('label: "2026-05-19 历史复盘"', html)

    def test_monitor_cards_align_header_with_content_edges(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn('headerClass = "px-4 md:px-6 py-3"', html)
        funnel_card = html[html.index("策略漏斗总览") : html.index("第 0 步：市场环境")]
        self.assertIn('headerClass="px-4 py-3"', funnel_card)
        self.assertIn('bodyClass="p-4 space-y-4"', funnel_card)
        self.assertIn("w-full min-w-0", html)
        self.assertIn("flex items-center gap-3 flex-wrap justify-end shrink-0", html)

    def test_monitor_scan_button_clicks_even_when_scan_is_unavailable(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn("const canRunScan = Boolean(appliedStrategy) && apiStatus.status === 'online';", html)
        self.assertIn("disabled={scanButtonDisabled}", html)
        self.assertIn("const scanButtonDisabled = hasStaticScan || isScanning;", html)
        self.assertIn("aria-disabled={!canRunScan || scanButtonDisabled}", html)
        self.assertIn("!appliedStrategy ? '请先在策略页应用一个策略'", html)
        self.assertNotIn("button onClick={handleRunScan} disabled={!canRunScan || isScanning}", html)

    def test_static_snapshot_mode_uses_read_only_controls(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn("const scanButtonText = hasStaticScan ? '只读快照' : isScanning ? '扫描中' : '执行扫描';", html)
        self.assertIn("const scanButtonDisabled = hasStaticScan || isScanning;", html)
        self.assertIn("disabled={scanButtonDisabled}", html)
        self.assertIn("hasStaticScan ? 'GitHub Pages 只展示最近一次收盘快照，等待收盘自动更新'", html)

        funnel_card = html[html.index("策略漏斗总览") : html.index("第 0 步：市场环境")]
        self.assertIn("hasStaticScan ? (", funnel_card)
        self.assertIn(">观察日期</span>", funnel_card)
        self.assertIn("{staticDate || '--'}", funnel_card)
        self.assertIn(": (", funnel_card)
        self.assertIn("<select value={currentDate}", funnel_card)

    def test_monitor_header_does_not_duplicate_data_source_notice(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn("const currentProvider =", html)
        self.assertIn("const dataSourceLabel = dataSourceName(currentProvider);", html)
        self.assertIn("数据源：${dataSourceLabel}", html)
        monitor_actions = html[html.index("actions={") : html.index("stats={", html.index("actions={"))]
        self.assertNotIn(">数据源</span>", monitor_actions)
        self.assertNotIn("当前数据源", monitor_actions)

    def test_toast_timer_is_reset_between_messages(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn("const toastTimerRef = useRef(null);", html)
        self.assertIn("if (toastTimerRef.current) clearTimeout(toastTimerRef.current);", html)
        self.assertIn("toastTimerRef.current = setTimeout(() => setToast(''), 3000);", html)


if __name__ == "__main__":
    unittest.main()
