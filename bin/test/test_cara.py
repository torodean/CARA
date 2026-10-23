#!/bin/python3
"""
 test_cara.py
 Created by: Antonius Torode
 Description: End-to-end regression tests for the CARA application flow.
"""
import sys
from unittest.mock import patch

from cara import main


def test_main_end_to_end(tmp_path):
    """
    Regression test for the full main() flow: with a configuration that does
    not set EXCLUDE_KEYWORDS/INCLUDE_KEYWORDS, commits must survive filtering
    and a changelog must be written even when fewer than three entries exist.
    """
    config_path = tmp_path / "cara.conf"
    config_path.write_text("MIN_WORDS = 2\nGROUP_BY = day\nOUTPUT_ENTRIES = message\n")

    output_path = tmp_path / "CHANGELOG.md"

    raw_lines = [
        "'abc1234567890|Alice|2025-08-12|Add new feature'",
        "'def9876543210|Bob|2025-08-11|Fix the parser'"
    ]
    full_date_lines = [
        "'abc1234567890|Alice|2025,08,12,Tuesday,August|Add new feature'",
        "'def9876543210|Bob|2025,08,11,Monday,August|Fix the parser'"
    ]

    original_argv = sys.argv
    sys.argv = ["cara", "-c", str(config_path), "-o", str(output_path), "-r", "."]
    try:
        with patch("subprocess.check_output",
                   side_effect=["\n".join(raw_lines), "\n".join(full_date_lines)]):
            main()
    finally:
        sys.argv = original_argv

    assert output_path.exists()
    content = output_path.read_text()
    assert "# Changelog" in content
    assert "## 2025-08-12 (Tuesday)" in content
    assert "Add new feature." in content
    assert "Fix the parser." in content
