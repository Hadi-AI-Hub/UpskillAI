"""Tests for layer0.store: JSONL log + marker-file I/O (Imperative Shell).

Seam: read_log/append_entry against a real (tmp) log.jsonl file, and
read_marker/write_marker/delete_marker against a real (tmp) marker file.
"""
from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from layer0.store import append_entry, delete_marker, read_log, read_marker, write_marker


class LogTests(unittest.TestCase):
    def test_read_log_missing_file_is_empty(self) -> None:
        with TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "log.jsonl"
            self.assertEqual(read_log(log_path), [])

    def test_append_then_read_round_trips(self) -> None:
        with TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "nested" / "log.jsonl"
            entry = {"date": "2026-09-11", "mission": "Intro to attention", "completed": True}
            append_entry(log_path, entry)
            self.assertEqual(read_log(log_path), [entry])

    def test_append_is_additive(self) -> None:
        with TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "log.jsonl"
            first = {"date": "2026-09-10", "completed": True}
            second = {"date": "2026-09-11", "completed": True}
            append_entry(log_path, first)
            append_entry(log_path, second)
            self.assertEqual(read_log(log_path), [first, second])


class MarkerTests(unittest.TestCase):
    def test_read_marker_missing_file_is_none(self) -> None:
        with TemporaryDirectory() as tmp:
            marker_path = Path(tmp) / ".in-progress.json"
            self.assertIsNone(read_marker(marker_path))

    def test_write_then_read_round_trips(self) -> None:
        with TemporaryDirectory() as tmp:
            marker_path = Path(tmp) / "nested" / ".in-progress.json"
            marker = {"date": "2026-09-11", "started_at": "2026-09-11T08:00:00-07:00", "target_minutes": 30}
            write_marker(marker_path, marker)
            self.assertEqual(read_marker(marker_path), marker)

    def test_delete_marker_removes_file(self) -> None:
        with TemporaryDirectory() as tmp:
            marker_path = Path(tmp) / ".in-progress.json"
            write_marker(marker_path, {"date": "2026-09-11"})
            delete_marker(marker_path)
            self.assertIsNone(read_marker(marker_path))

    def test_delete_marker_missing_file_is_a_noop(self) -> None:
        with TemporaryDirectory() as tmp:
            marker_path = Path(tmp) / ".in-progress.json"
            delete_marker(marker_path)  # should not raise


if __name__ == "__main__":
    unittest.main()
