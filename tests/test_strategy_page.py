from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class StrategyPageTest(unittest.TestCase):
    def test_strategy_page_persists_selected_card_between_tab_switches(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn("const [activeCardId, setActiveCardId] = useStickyState(appliedId || strategies[0]?.id || null, 'lq_activeStrategyCardId');", html)
        self.assertIn("const hasActiveStrategy = strategies.some(s => s.id === activeCardId);", html)
        self.assertNotIn("const [activeCardId, setActiveCardId] = useState(strategies[0]?.id);", html)

    def test_applying_strategy_keeps_it_selected(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        handle_apply = html[html.index("const handleApply = () => {") : html.index("const handleCancelApply = () => {")]

        self.assertIn("setActiveCardId(activeStrategy.id);", handle_apply)
        self.assertIn("setAppliedId(activeStrategy.id);", handle_apply)


if __name__ == "__main__":
    unittest.main()
