"""Tests for layer0.state_machine: the streak state machine (Functional Core).

Seam: the pure functions compute_streak_state, compute_longest_streak,
and current_streak_length, called with a set of completed dates and
"today" — no file I/O, no clock.
"""
from __future__ import annotations

import unittest
from datetime import date

from layer0.state_machine import (
    compute_longest_streak,
    compute_streak_state,
    current_streak_length,
)


def d(iso: str) -> date:
    return date.fromisoformat(iso)


class ComputeStreakStateTests(unittest.TestCase):
    def test_no_prior_log_is_active(self) -> None:
        self.assertEqual(compute_streak_state(set(), d("2026-09-11")), "active")

    def test_today_already_completed_is_active(self) -> None:
        completed = {d("2026-09-11")}
        self.assertEqual(compute_streak_state(completed, d("2026-09-11")), "active")

    def test_today_missing_yesterday_completed_is_active(self) -> None:
        completed = {d("2026-09-10")}
        self.assertEqual(compute_streak_state(completed, d("2026-09-11")), "active")

    def test_yesterday_missing_day_before_completed_is_grace(self) -> None:
        completed = {d("2026-09-09")}
        self.assertEqual(compute_streak_state(completed, d("2026-09-11")), "grace")

    def test_two_consecutive_missed_days_is_broken(self) -> None:
        completed = {d("2026-09-08")}
        self.assertEqual(compute_streak_state(completed, d("2026-09-11")), "broken")


class ComputeLongestStreakTests(unittest.TestCase):
    def test_empty_log_is_zero(self) -> None:
        self.assertEqual(compute_longest_streak(set()), 0)

    def test_single_day_is_one(self) -> None:
        self.assertEqual(compute_longest_streak({d("2026-09-11")}), 1)

    def test_consecutive_run_counted(self) -> None:
        completed = {d("2026-09-09"), d("2026-09-10"), d("2026-09-11")}
        self.assertEqual(compute_longest_streak(completed), 3)

    def test_longest_of_multiple_runs(self) -> None:
        completed = {
            d("2026-09-01"),
            d("2026-09-02"),
            d("2026-09-05"),
            d("2026-09-06"),
            d("2026-09-07"),
        }
        self.assertEqual(compute_longest_streak(completed), 3)


class CurrentStreakLengthTests(unittest.TestCase):
    def test_broken_streak_is_zero(self) -> None:
        completed = {d("2026-09-08")}
        self.assertEqual(current_streak_length(completed, d("2026-09-11")), 0)

    def test_active_streak_counts_back_from_today(self) -> None:
        completed = {d("2026-09-09"), d("2026-09-10"), d("2026-09-11")}
        self.assertEqual(current_streak_length(completed, d("2026-09-11")), 3)

    def test_active_streak_counts_back_from_yesterday_when_today_not_logged(
        self,
    ) -> None:
        completed = {d("2026-09-09"), d("2026-09-10")}
        self.assertEqual(current_streak_length(completed, d("2026-09-11")), 2)

    def test_grace_streak_counts_back_from_day_before_yesterday(self) -> None:
        completed = {d("2026-09-08"), d("2026-09-09")}
        self.assertEqual(current_streak_length(completed, d("2026-09-11")), 2)


if __name__ == "__main__":
    unittest.main()
