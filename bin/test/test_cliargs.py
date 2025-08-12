# test_cliargs.py
import sys
import pytest
from pathlib import Path

sys.path.append('../')

from cara import CLIArgs  # Replace with actual module name


def run_cli_with_args(args):
    """
    Helper function to create a CLIArgs instance using mocked command-line arguments.

    Args:
        args (list[str]): List of arguments to simulate, excluding the program name.

    Returns:
        CLIArgs: An initialized CLIArgs object with parsed values.
    """
    original_argv = sys.argv
    sys.argv = ["prog"] + args
    try:
        return CLIArgs()
    finally:
        sys.argv = original_argv


def test_no_arguments_defaults():
    """
    Test that CLIArgs sets all values to defaults when no arguments are provided.
    """
    cli = run_cli_with_args([])
    assert cli.verbose is False
    assert cli.debug is False
    assert cli.config == "cara.conf"
    assert cli.input_file is None
    assert cli.output_file == "CHANGELOG.md"
    assert cli.repo_path == "."


@pytest.mark.parametrize("flag, attr, expected", [
    (["--verbose"], "verbose", True),
    (["--debug"], "debug", True),
    (["--config", "myconfig.conf"], "config", "myconfig.conf"),
    (["--input", "input.md"], "input_file", "input.md"),
    (["--output", "out.md"], "output_file", "out.md"),
    (["--repo", "/tmp/repo"], "repo_path", "/tmp/repo"),
])
def test_each_flag_individually(flag, attr, expected):
    """
    Test that each CLI flag correctly sets the corresponding attribute when provided individually.
    """
    cli = run_cli_with_args(flag)
    assert getattr(cli, attr) == expected


def test_multiple_flags_together():
    """
    Test that multiple CLI flags provided together set all corresponding attributes correctly.
    """
    cli = run_cli_with_args([
        "--verbose",
        "--debug",
        "--config", "cfg.conf",
        "--input", "in.md",
        "--output", "out.md",
        "--repo", "/tmp/repo"
    ])
    assert cli.verbose is True
    assert cli.debug is True
    assert cli.config == "cfg.conf"
    assert cli.input_file == "in.md"
    assert cli.output_file == "out.md"
    assert cli.repo_path == "/tmp/repo"


def test_defaults_when_some_args_omitted():
    """
    Test that CLIArgs sets defaults for omitted arguments when some arguments are provided.
    """
    cli = run_cli_with_args(["--verbose", "--input", "in.md"])
    assert cli.verbose is True
    assert cli.debug is False  # default
    assert cli.config == "cara.conf"  # default
    assert cli.input_file == "in.md"
    assert cli.output_file == "CHANGELOG.md"  # default
    assert cli.repo_path == "."  # default
