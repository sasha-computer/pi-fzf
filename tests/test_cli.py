"""Tests for CLI subcommands."""

import subprocess


def test_version() -> None:
    result = subprocess.run(
        ["uv", "run", "pi-fzf", "version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "pi-fzf v" in result.stdout


def test_help() -> None:
    result = subprocess.run(
        ["uv", "run", "pi-fzf", "help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "fuzzy find" in result.stdout.lower()


def test_init_fish() -> None:
    result = subprocess.run(
        ["uv", "run", "pi-fzf", "init", "fish"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "pi-fzf-widget" in result.stdout


def test_init_unknown_shell() -> None:
    result = subprocess.run(
        ["uv", "run", "pi-fzf", "init", "powershell"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "Unknown shell" in result.stderr
