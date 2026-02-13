"""Tests for session JSONL parsing."""

from pathlib import Path

from pi_fzf.sessions import extract_text, parse_header, parse_messages, session_cwd


def test_extract_text_string() -> None:
    assert extract_text("hello world") == "hello world"


def test_extract_text_string_whitespace() -> None:
    assert extract_text("  trimmed  ") == "trimmed"


def test_extract_text_content_blocks() -> None:
    blocks = [{"type": "text", "text": "block content"}]
    assert extract_text(blocks) == "block content"


def test_extract_text_skips_non_text_blocks() -> None:
    blocks = [{"type": "image", "data": "abc"}, {"type": "text", "text": "found it"}]
    assert extract_text(blocks) == "found it"


def test_extract_text_empty_blocks() -> None:
    blocks = [{"type": "image", "data": "abc"}]
    assert extract_text(blocks) == ""


def test_extract_text_empty_string() -> None:
    assert extract_text("") == ""


def test_extract_text_none() -> None:
    assert extract_text(None) == ""


def test_extract_text_number() -> None:
    assert extract_text(42) == ""


def test_parse_header_valid() -> None:
    line = (
        '{"type":"session","version":1,"id":"abc",'
        '"timestamp":"2025-12-01T10:30:00.000Z","cwd":"/tmp"}'
    )
    header = parse_header(line)
    assert header is not None
    assert header.cwd == "/tmp"
    assert header.id == "abc"


def test_parse_header_not_session() -> None:
    line = '{"type":"message","message":{}}'
    assert parse_header(line) is None


def test_parse_header_invalid_json() -> None:
    assert parse_header("{invalid}") is None


def test_parse_messages_valid(testdata: Path) -> None:
    header, messages = parse_messages(testdata / "valid_session.jsonl")
    assert header is not None
    assert header.cwd == "/Users/test/projects/myapp"

    # Should have both user and assistant messages
    user_msgs = [m for m in messages if m.role == "user"]
    assistant_msgs = [m for m in messages if m.role == "assistant"]
    assert len(user_msgs) == 3
    assert len(assistant_msgs) == 2

    assert "Fix the login bug" in user_msgs[0].text
    assert "rate limiting" in user_msgs[1].text
    assert "Deploy to staging" in user_msgs[2].text
    assert "auth.ts" in assistant_msgs[0].text
    assert "rate limiting" in assistant_msgs[1].text


def test_parse_messages_empty_session(testdata: Path) -> None:
    header, messages = parse_messages(testdata / "empty_session.jsonl")
    assert header is not None
    assert messages == []


def test_parse_messages_no_text_content(testdata: Path) -> None:
    """Image-only user message should be skipped, assistant text kept."""
    header, messages = parse_messages(testdata / "no_text_content.jsonl")
    assert header is not None
    # User message has no text (image only) — skipped
    # Assistant message has text — kept
    user_msgs = [m for m in messages if m.role == "user"]
    assistant_msgs = [m for m in messages if m.role == "assistant"]
    assert len(user_msgs) == 0
    assert len(assistant_msgs) == 1
    assert "I can see the image" in assistant_msgs[0].text


def test_parse_messages_assistant_has_keywords(testdata: Path) -> None:
    """Assistant messages with specific keywords should be findable."""
    header, messages = parse_messages(testdata / "assistant_has_keywords.jsonl")
    assert header is not None

    all_text = " ".join(m.text for m in messages)
    assert "IKKEGOL" in all_text
    assert "foot pedal" in all_text

    # The user never said "IKKEGOL" — only the assistant did
    user_text = " ".join(m.text for m in messages if m.role == "user")
    assert "IKKEGOL" not in user_text

    assistant_text = " ".join(m.text for m in messages if m.role == "assistant")
    assert "IKKEGOL" in assistant_text


def test_session_cwd(testdata: Path) -> None:
    cwd = session_cwd(testdata / "valid_session.jsonl")
    assert cwd == "/Users/test/projects/myapp"


def test_session_cwd_nonexistent() -> None:
    cwd = session_cwd(Path("/nonexistent/file.jsonl"))
    assert cwd == ""
