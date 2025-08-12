#!/bin/python3
"""
 test_gitlog.py
 Created by: Antonius Torode
 Description: This file tests the GitLog and GitLogEntry classes of CARA.
"""
import sys
from unittest.mock import patch
import pytest

sys.path.append('../')

from cara import GitLog, GitLogEntry, Config

def make_entry(commit="abc1234567890", author="Author", full_date="2025,08,12,Tuesday,August",
               display_date="2025-08-12", message="Test commit message"):
    """
    Helper to create a GitLogEntry instance with default values.
    """
    return GitLogEntry(commit, author, full_date, display_date, message)


def test_gitlogentry_repr():
    """
    Test that GitLogEntry __repr__ returns the expected short format.
    """
    entry = make_entry()
    assert repr(entry) == "<abc1234 - Author - 2025-08-12>"


def test_apply_filters_min_words():
    """
    Test that apply_filters() filters out entries with fewer words than MIN_WORDS.
    """
    config = Config()
    config.set("MIN_WORDS", "3")
    log = GitLog(config)
    log.entries = [make_entry(message="one two"), make_entry(message="one two three")]
    log.apply_filters()
    assert all(len(e.message.split()) >= 3 for e in log.entries)


def test_apply_filters_min_chars():
    """
    Test that apply_filters() filters out entries with fewer characters than MIN_CHARS.
    """
    config = Config()
    config.set("MIN_CHARS", "10")
    log = GitLog(config)
    log.entries = [make_entry(message="short"), make_entry(message="long enough message")]
    log.apply_filters()
    assert all(len(e.message) >= 10 for e in log.entries)


def test_apply_filters_exclude_keywords():
    """
    Test that apply_filters() removes entries containing excluded keywords.
    """
    config = Config()
    config.set("EXCLUDE_KEYWORDS", "skip")
    log = GitLog(config)
    log.entries = [make_entry(message="skip this commit"), make_entry(message="keep this one")]
    log.apply_filters()
    assert all("skip" not in e.message.lower() for e in log.entries)


def test_apply_filters_include_keywords():
    """
    Test that apply_filters() only keeps entries containing at least one included keyword.
    """
    config = Config()
    config.set("INCLUDE_KEYWORDS", "feature")
    log = GitLog(config)
    log.entries = [make_entry(message="new feature added"), make_entry(message="fix bug")]
    log.apply_filters()
    assert all("feature" in e.message.lower() for e in log.entries)


@patch("subprocess.check_output")
def test_parse_log(mock_check_output):
    """
    Test that parse_log() populates entries correctly from mocked git log output.
    """
    config = Config()
    log = GitLog(config, repo_path=".")

    raw_lines = [
        "'abc1234567890|Author|2025-08-12|Commit message 1'",
        "'def9876543210|Author|2025-08-13|Commit message 2'"
    ]
    full_date_lines = [
        "'abc1234567890|Author|2025,08,12,Tuesday,August|Commit message 1'",
        "'def9876543210|Author|2025,08,13,Wednesday,August|Commit message 2'"
    ]

    mock_check_output.side_effect = [
        "\n".join(raw_lines),
        "\n".join(full_date_lines)
    ]

    log.parse_log()

    assert len(log.entries) == 2
    assert log.entries[0].commit == "abc1234567890"
    assert log.entries[0].full_date == "2025,08,12,Tuesday,August"
    assert log.entries[0].message == "Commit message 1"


def test_remove_duplicates_by_day_and_message():
    """
    Test that remove_duplicates_by_day_and_message() removes entries with same date and message.
    """
    log = GitLog()
    entries = [
        make_entry(display_date="2025-08-12", message="Same message"),
        make_entry(display_date="2025-08-12", message="Same message"),
        make_entry(display_date="2025-08-13", message="Different message")
    ]
    result = log.remove_duplicates_by_day_and_message(entries)
    assert len(result) == 2
    dates_messages = {(e.display_date, e.message) for e in result}
    assert len(dates_messages) == 2


def test_print_entries(capsys):
    """
    Test that print_entries() outputs formatted entry lines.
    """
    log = GitLog()
    log.entries = [make_entry()]
    log.print_entries()
    captured = capsys.readouterr()
    assert "2025,08,12,Tuesday,August | Author | abc1234 - Test commit message" in captured.out
