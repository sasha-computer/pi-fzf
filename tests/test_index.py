"""Tests for the fzf entry index."""

import shutil
from pathlib import Path

import pytest

from pi_fzf.index import list_entries


@pytest.fixture
def sessions_env(testdata: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Set up a temporary PI_CODING_AGENT_DIR with a sessions/ subdirectory."""
    sessions_dir = tmp_path / "sessions"
    sessions_dir.mkdir()
    monkeypatch.setenv("PI_CODING_AGENT_DIR", str(tmp_path))
    return sessions_dir


def _copy_fixture(testdata: Path, sessions_dir: Path, name: str) -> None:
    shutil.copy(testdata / name, sessions_dir / name)


def test_list_entries_valid_session(testdata: Path, sessions_env: Path) -> None:
    _copy_fixture(testdata, sessions_env, "valid_session.jsonl")
    entries = list_entries()

    # Should have: 1 summary + 3 user + 2 assistant = 6 entries
    assert len(entries) == 6

    summaries = [e for e in entries if e.role == "summary"]
    assert len(summaries) == 1
    assert "📋" in summaries[0].display
    assert "3 msgs" in summaries[0].display

    user_entries = [e for e in entries if e.role == "user"]
    assert len(user_entries) == 3

    assistant_entries = [e for e in entries if e.role == "assistant"]
    assert len(assistant_entries) == 2


def test_list_entries_includes_assistant_text(testdata: Path, sessions_env: Path) -> None:
    """The key improvement: assistant messages are now searchable."""
    _copy_fixture(testdata, sessions_env, "assistant_has_keywords.jsonl")
    entries = list_entries()

    all_display = " ".join(e.display for e in entries)
    assert "IKKEGOL" in all_display
    assert "foot pedal" in all_display

    # Verify it's tagged as PI
    pi_entries = [e for e in entries if e.role == "assistant"]
    pi_text = " ".join(e.display for e in pi_entries)
    assert "[PI]" in pi_text
    assert "IKKEGOL" in pi_text


def test_list_entries_empty_session(testdata: Path, sessions_env: Path) -> None:
    _copy_fixture(testdata, sessions_env, "empty_session.jsonl")
    entries = list_entries()
    # Empty session still gets a summary entry (0 msgs)
    assert len(entries) == 1
    assert entries[0].role == "summary"
    assert "0 msgs" in entries[0].display


def test_list_entries_no_text_content(testdata: Path, sessions_env: Path) -> None:
    _copy_fixture(testdata, sessions_env, "no_text_content.jsonl")
    entries = list_entries()
    # 1 summary + 1 assistant (user had image only, no text)
    assert len(entries) == 2
    roles = {e.role for e in entries}
    assert "assistant" in roles
    assert "summary" in roles


def test_list_entries_multiple_sessions_sorted(testdata: Path, sessions_env: Path) -> None:
    _copy_fixture(testdata, sessions_env, "valid_session.jsonl")
    _copy_fixture(testdata, sessions_env, "multi_session.jsonl")
    entries = list_entries()

    # multi_session (Dec 5) is newer than valid_session (Dec 1)
    # Newest entries should come first
    non_summary = [e for e in entries if e.role != "summary"]
    first = non_summary[0]
    assert "api" in first.display or "migration" in first.display.lower()


def test_list_entries_no_sessions_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PI_CODING_AGENT_DIR", str(tmp_path))
    # No sessions/ subdirectory at all
    entries = list_entries()
    assert entries == []


def test_list_entries_role_tags(testdata: Path, sessions_env: Path) -> None:
    _copy_fixture(testdata, sessions_env, "valid_session.jsonl")
    entries = list_entries()

    user_entries = [e for e in entries if e.role == "user"]
    assistant_entries = [e for e in entries if e.role == "assistant"]

    for e in user_entries:
        assert "[YOU]" in e.display
    for e in assistant_entries:
        assert "[PI]" in e.display
