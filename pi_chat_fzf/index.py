"""Build the searchable entry list from all Pi sessions."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from pi_chat_fzf.sessions import parse_messages


@dataclass
class FzfEntry:
    file_path: str
    role: str  # "user" or "assistant"
    msg_index: int
    sort_key: str  # ISO timestamp for sorting
    display: str


def sessions_dir() -> Path:
    """Return the path to the Pi sessions directory."""
    env = os.environ.get("PI_CODING_AGENT_DIR")
    if env:
        return Path(env) / "sessions"
    return Path.home() / ".pi" / "agent" / "sessions"


def _format_timestamp(ts: str) -> tuple[str, str]:
    """Parse a timestamp string, return (display, sort_key)."""
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            dt = datetime.strptime(ts, fmt)  # noqa: DTZ007
            return dt.strftime("%b %d %H:%M"), dt.isoformat()
        except ValueError:
            continue
    # Fallback: use raw timestamp
    return ts[:16], ts


def _shorten_home(path: str) -> str:
    home = str(Path.home())
    if path.startswith(home):
        return "~" + path[len(home) :]
    return path


def list_entries() -> list[FzfEntry]:
    """Scan all session files and build the fzf entry list.

    Indexes both user and assistant messages so that assistant-side
    keywords (like product names, recommendations) are searchable.
    """
    root = sessions_dir()
    if not root.exists():
        return []

    entries: list[FzfEntry] = []

    for path in root.rglob("*.jsonl"):
        header, messages = parse_messages(path)
        if header is None:
            continue

        short_cwd = _shorten_home(header.cwd)
        nice_ts, sort_ts = _format_timestamp(header.timestamp)

        # Session summary entry — always appears, uses first user message as summary
        user_count = sum(1 for m in messages if m.role == "user")
        first_user = next((m.text for m in messages if m.role == "user"), "")
        summary_text = " ".join(first_user.split())
        if len(summary_text) > 120:
            summary_text = summary_text[:120]
        summary = f"{nice_ts}  {short_cwd}  │  📋 {user_count} msgs · {summary_text}"
        entries.append(
            FzfEntry(
                file_path=str(path),
                role="summary",
                msg_index=0,
                sort_key=sort_ts + "_summary",
                display=summary,
            )
        )

        for msg in messages:
            text = " ".join(msg.text.split())  # flatten whitespace
            max_len = 150 if msg.role == "assistant" else 200
            if len(text) > max_len:
                text = text[:max_len]

            role_tag = "YOU" if msg.role == "user" else "PI"
            display = f"{nice_ts}  {short_cwd}  │  [{role_tag}] {text}"
            entries.append(
                FzfEntry(
                    file_path=str(path),
                    role=msg.role,
                    msg_index=msg.index,
                    sort_key=sort_ts,
                    display=display,
                )
            )

    # Sort newest first; within same session, summary first then messages by index desc
    entries.sort(key=lambda e: (e.sort_key, e.msg_index), reverse=True)

    return entries
