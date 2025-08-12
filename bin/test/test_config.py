#!/bin/python3
"""
 test_config.py
 Created by: Antonius Torode
 Description: This file tests the Config class of CARA.
"""
import sys
import tempfile
import pytest

sys.path.append('../')

from cara import Config


def create_temp_config(content):
    """
    Helper to create a temporary configuration file.

    Args:
        content (str): The configuration file content.

    Returns:
        str: Path to the temporary configuration file.
    """
    tmp = tempfile.NamedTemporaryFile(mode='w', delete=False)
    tmp.write(content)
    tmp.flush()
    return tmp.name


def test_load_valid_config():
    """
    Test that a valid configuration file is loaded correctly.
    """
    cfg_path = create_temp_config("KEY1=VALUE1\nKEY2=VALUE2\n")
    config = Config(cfg_path)
    assert config.get("KEY1") == "VALUE1"
    assert config.get("KEY2") == "VALUE2"


def test_comments_and_empty_lines():
    """
    Test that comments and empty lines are ignored when loading config.
    """
    cfg_path = create_temp_config("""
# This is a comment
KEY1=VALUE1

KEY2=VALUE2 # inline comment
""")
    config = Config(cfg_path)
    assert config.get("KEY1") == "VALUE1"
    assert config.get("KEY2") == "VALUE2"
    assert config.get("KEY3") is None


def test_malformed_lines_skipped():
    """
    Test that malformed lines without the delimiter are skipped.
    """
    cfg_path = create_temp_config("KEY1 VALUE1\nKEY2=VALUE2\n")
    config = Config(cfg_path)
    assert config.get("KEY1") is None
    assert config.get("KEY2") == "VALUE2"


def test_get_with_default_value():
    """
    Test that get() returns the provided default for missing keys.
    """
    config = Config()
    assert config.get("MISSING", default="default_val") == "default_val"


def test_set_and_get_value():
    """
    Test that set() correctly stores a value retrievable by get().
    """
    config = Config()
    config.set("NEWKEY", "NEWVALUE")
    assert config.get("NEWKEY") == "NEWVALUE"


def test_print_config_empty(capsys):
    """
    Test that print_config() outputs 'No configuration loaded.' when empty.
    """
    config = Config()
    config.print_config()
    captured = capsys.readouterr()
    assert "No configuration loaded." in captured.out


def test_print_config_with_values(capsys):
    """
    Test that print_config() prints all key-value pairs when populated.
    """
    config = Config()
    config.set("KEY1", "VALUE1")
    config.set("KEY2", "VALUE2")
    config.print_config()
    captured = capsys.readouterr()
    assert "Current Configuration:" in captured.out
    assert "KEY1 = VALUE1" in captured.out
    assert "KEY2 = VALUE2" in captured.out
