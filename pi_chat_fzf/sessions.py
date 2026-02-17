"""Parse Pi coding agent session JSONL files."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class SessionHeader:
    type: str
    version: int
    id: str
    timestamp: str
    cwd: str


@dataclass
class Message:
    role: str  # "user" or "assistant"
    text: str
    index: int  # index within the role (e.g. 3rd user message = 2)


def parse_header(line: str) -> SessionHeader | None:
    """Parse the first line of a JSONL session file."""
    try:
        data = json.loads(line)
    except json.JSONDecodeError:
        return None
    if data.get("type") != "session":
        return None
    return SessionHeader(
        type=data["type"],
        version=data.get("version", 1),
        id=data.get("id", ""),
        timestamp=data.get("timestamp", ""),
        cwd=data.get("cwd", ""),
    )


def extract_text(content: Any) -> str:
    """Extract text from a message content field.

    Content can be a plain string or an array of content blocks
    like [{"type": "text", "text": "..."}].
    """
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text", "").strip()
                if text:
                    return text

    return ""


def parse_messages(path: Path) -> tuple[SessionHeader | None, list[Message]]:
    """Parse a session file, returning the header and all messages with text content."""
    lines = path.read_text().splitlines()
    if not lines:
        return None, []

    header = parse_header(lines[0])
    if header is None:
        return None, []

    messages: list[Message] = []
    user_idx = 0
    assistant_idx = 0

    for line in lines[1:]:
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue

        if data.get("type") != "message":
            continue

        msg_data = data.get("message", {})
        role = msg_data.get("role", "")
        if role not in ("user", "assistant"):
            continue

        text = extract_text(msg_data.get("content", ""))
        if not text:
            if role == "user":
                user_idx += 1
            elif role == "assistant":
                assistant_idx += 1
            continue

        idx = user_idx if role == "user" else assistant_idx
        messages.append(Message(role=role, text=text, index=idx))

        if role == "user":
            user_idx += 1
        else:
            assistant_idx += 1

    return header, messages


def session_cwd(path: Path) -> str:
    """Read just the cwd from a session file header."""
    try:
        first_line = path.read_text().split("\n", 1)[0]
    except OSError:
        return ""
    header = parse_header(first_line)
    return header.cwd if header else ""
