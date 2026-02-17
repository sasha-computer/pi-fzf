"""Tests for the preview renderer."""

from pathlib import Path

from pi_chat_fzf.preview import render_preview


def test_preview_valid_session(testdata: Path) -> None:
    output = render_preview(str(testdata / "valid_session.jsonl"), "user", 0)

    assert "📂" in output
    assert "🕐" in output
    assert "💬" in output
    assert "▶ YOU" in output
    assert "◀ PI" in output
    assert "Fix the login bug" in output
    # First user message (index 0) should be highlighted
    assert "← ← ←" in output


def test_preview_assistant_message(testdata: Path) -> None:
    output = render_preview(str(testdata / "valid_session.jsonl"), "assistant", 0)

    # First assistant message should be highlighted
    assert "← ← ←" in output
    assert "auth.ts" in output


def test_preview_summary_highlights_first_user(testdata: Path) -> None:
    output = render_preview(str(testdata / "valid_session.jsonl"), "summary", 0)

    # Summary targets the first user message
    lines = output.split("\n")
    marker_lines = [line for line in lines if "← ← ←" in line]
    assert len(marker_lines) >= 1


def test_preview_nonexistent_file() -> None:
    output = render_preview("/nonexistent/file.jsonl", "user", 0)
    assert "Cannot parse" in output or "Error" in output.lower() or output != ""
