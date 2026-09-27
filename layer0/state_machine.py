"""Functional Core: pure functions deriving streak state from a set of
completed dates. No file I/O, no clock reads — callers pass `today` in.

Streak state machine (locked in the wayfinder map):
    active -> grace after 1 missed day -> broken after 2 consecutive missed days.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Literal

ONE_DAY = timedelta(days=1)

StreakState = Literal["active", "grace", "broken"]


def completed_dates_from_entries(entries: list[dict[str, Any]]) -> set[date]:
    """Extract the set of completed dates from a list of daily log entries."""
    return {date.fromisoformat(e["date"]) for e in entries}


def _classify(completed_dates: set[date], today: date) -> tuple[StreakState, date | None]:
    """Return (streak_state, anchor) as of `today`.

    `anchor` is the most recent day the current streak run should be counted
    back from (today, yesterday, or the day before), or None once broken.
    Single source of truth for the state machine's branching so
    compute_streak_state and current_streak_length can't drift apart.
    """
    if not completed_dates:
        return "active", today
    if today in completed_dates:
        return "active", today
    if today - ONE_DAY in completed_dates:
        return "active", today - ONE_DAY
    if today - 2 * ONE_DAY in completed_dates:
        return "grace", today - 2 * ONE_DAY
    return "broken", None


def compute_streak_state(completed_dates: set[date], today: date) -> StreakState:
    """Return "active", "grace", or "broken" as of `today`.

    Evaluated by walking backward from today: today or yesterday completed
    means the streak is still active (today isn't over yet); the day before
    yesterday completed (but not yesterday) is one missed day (grace); two
    consecutive missed days is broken. An empty log is active by default.
    """
    state, _ = _classify(completed_dates, today)
    return state


def compute_longest_streak(completed_dates: set[date]) -> int:
    """Return the length of the longest run of consecutive completed days."""
    longest = 0
    current = 0
    previous: date | None = None
    for day in sorted(completed_dates):
        if previous is not None and day - previous == ONE_DAY:
            current += 1
        else:
            current = 1
        longest = max(longest, current)
        previous = day
    return longest


def current_streak_length(completed_dates: set[date], today: date) -> int:
    """Return the length of the streak currently in progress as of `today`.

    Zero once broken. Otherwise counts consecutive completed days backward
    from the anchor day implied by the streak state (today, yesterday, or
    the day before — see _classify).
    """
    _, anchor = _classify(completed_dates, today)
    if anchor is None:
        return 0

    length = 0
    day = anchor
    while day in completed_dates:
        length += 1
        day -= ONE_DAY
    return length
