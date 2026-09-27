"""Tests for layer0.dashboard: static HTML rendering from log entries.

Seam: render_dashboard(entries, today) -> html string. Checks the derived
values (streak state, streak count, longest streak, inlined data) actually
land in the output, without pinning exact markup.
"""
from __future__ import annotations

import json
import unittest
from datetime import date

from layer0.dashboard import render_dashboard


class RenderDashboardTests(unittest.TestCase):
    def test_empty_log_renders_without_error(self) -> None:
        html = render_dashboard([], today=date(2026, 9, 11))
        self.assertIn("<svg", html)
        self.assertIn("<script", html)

    def test_inlines_entries_as_script_data_literal(self) -> None:
        entries = [
            {
                "date": "2026-09-11",
                "mission": "Intro to attention mechanisms",
                "target_minutes": 30,
                "started_at": "2026-09-11T08:00:00-07:00",
                "completed_at": "2026-09-11T08:30:00-07:00",
                "completed": True,
                "exercise": None,
                "streak_state": "active",
            }
        ]
        html = render_dashboard(entries, today=date(2026, 9, 11))
        start = html.index("[", html.index("const upskillData = "))
        end = html.index("]", start) + 1
        inlined = json.loads(html[start:end])
        self.assertEqual(inlined, entries)

    def test_shows_current_streak_and_longest_streak(self) -> None:
        entries = [
            {
                "date": iso,
                "mission": "m",
                "target_minutes": 30,
                "started_at": f"{iso}T08:00:00-07:00",
                "completed_at": f"{iso}T08:30:00-07:00",
                "completed": True,
                "exercise": None,
                "streak_state": "active",
            }
            for iso in ("2026-09-09", "2026-09-10", "2026-09-11")
        ]
        html = render_dashboard(entries, today=date(2026, 9, 11))
        self.assertIn(">3<", html)  # current streak and longest streak both 3

    def test_shows_streak_state(self) -> None:
        html = render_dashboard([], today=date(2026, 9, 11))
        self.assertIn("active", html)


if __name__ == "__main__":
    unittest.main()
