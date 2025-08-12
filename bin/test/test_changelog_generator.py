#!/bin/python3
"""
test_changelog_generator.py
Created by: Antonius Torode
Description: Tests the ChangelogGenerator class of CARA.
"""
import sys
import datetime
from collections import defaultdict
import pytest
from pathlib import Path

sys.path.append('../')

from cara import ChangelogGenerator, GitLogEntry  # Replace with actual module paths


class DummyConfig:
    """
    A simple dummy config for testing purposes.
    """
    def __init__(self, data):
        self.data = data

    def get(self, key, default=None):
        return self.data.get(key, default)


class DummyGitLog:
    """
    A dummy GitLog to simulate entries for ChangelogGenerator tests.
    """
    def __init__(self, entries):
        self._entries = entries

    def get_entries(self):
        return self._entries


def make_entry(commit, author, full_date, display_date, message):
    """
    Helper to create a GitLogEntry instance.
    """
    return GitLogEntry(commit, author, full_date, display_date, message)


def test_format_entry_all_fields():
    """
    Test that format_entry formats with 'all' output_entries config.
    """
    config = DummyConfig({"OUTPUT_ENTRIES": "all"})
    entry = make_entry("abc1234", "Alice", "2024,08,12,Monday,August", "2024-08-12", "Initial commit")
    gen = ChangelogGenerator(DummyGitLog([entry]), config)
    formatted = gen.format_entry(entry)
    assert formatted == "abc1234: Alice -> Initial commit."


@pytest.mark.parametrize("fields, expected", [
    ("date", "- [2024-08-12]."),
    ("commit", "- abc1234:"),
    ("author", "- Alice ->"),
    ("message", "- Initial commit."),
    ("date commit author message", "- [2024-08-12] abc1234: Alice -> Initial commit."),
])
def test_format_entry_partial(fields, expected):
    """
    Test format_entry with different OUTPUT_ENTRIES configurations.
    """
    config = DummyConfig({"OUTPUT_ENTRIES": fields})
    entry = make_entry("abc1234", "Alice", "2024,08,12,Monday,August", "2024-08-12", "Initial commit")
    gen = ChangelogGenerator(DummyGitLog([entry]), config)
    formatted = gen.format_entry(entry)
    assert formatted.startswith(expected)


@pytest.mark.parametrize("unit,key_format", [
    ("day", "%Y-%m-%d"),
    ("week", "%Y-W%W"),
    ("month", "%Y-%m"),
    ("year", "%Y"),
])
def test_group_by_time_unit(unit, key_format):
    """
    Test group_by_time_unit correctly groups entries by different units.
    """
    entry1 = make_entry("abc1234", "Alice", "2024,08,12,Monday,August", "2024-08-12", "Commit one")
    entry2 = make_entry("def5678", "Bob", "2024,08,13,Tuesday,August", "2024-08-13", "Commit two")
    gen = ChangelogGenerator(DummyGitLog([entry1, entry2]), DummyConfig({}))
    grouped = gen.group_by_time_unit(unit)
    assert isinstance(grouped, dict)
    assert all(isinstance(k, str) for k in grouped.keys())


def test_group_by_time_unit_invalid():
    """
    Test that group_by_time_unit raises ValueError for invalid units.
    """
    gen = ChangelogGenerator(DummyGitLog([]), DummyConfig({}))
    with pytest.raises(ValueError):
        gen.group_by_time_unit("invalid")


def test_generate_day_grouping():
    """
    Test that generate produces correct section headers for daily grouping.
    """
    entry = make_entry("abc1234", "Alice", "2024,08,12,Monday,August", "2024-08-12", "Commit message")
    config = DummyConfig({"GROUP_BY": "day", "OUTPUT_ENTRIES": "message"})
    gen = ChangelogGenerator(DummyGitLog([entry]), config)
    output = gen.generate()
    assert "# Changelog" in output
    assert "## 2024-08-12 (Monday)" in output
    assert "Commit message" in output


def test_write_to_file(tmp_path):
    """
    Test that write_to_file writes the generated changelog to a file.
    """
    entry = make_entry("abc1234", "Alice", "2024,08,12,Monday,August", "2024-08-12", "Commit message")
    config = DummyConfig({"GROUP_BY": "day", "OUTPUT_ENTRIES": "message"})
    gen = ChangelogGenerator(DummyGitLog([entry]), config)

    file_path = tmp_path / "CHANGELOG.md"
    gen.write_to_file(file_path)
    assert file_path.exists()
    content = file_path.read_text()
    assert "Commit message" in content
