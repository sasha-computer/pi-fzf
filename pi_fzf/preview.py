"""Render the preview pane for a selected fzf entry."""

from __future__ import annotations

from pathlib import Path

from pi_fzf.sessions import parse_messages


def _shorten_home(path: str) -> str:
    home = str(Path.home())
    if path.startswith(home):
        return "~" + path[len(home) :]
    return path


def render_preview(file_path: str, role: str, msg_index: int) -> str:
    """Render the full conversation preview for a session file.

    Highlights the target message (matching role + index) with an arrow marker.
    """
    path = Path(file_path)
    if not path.exists():
        return f"Cannot open: {file_path}"

    header, messages = parse_messages(path)
    if header is None:
        return f"Cannot parse session: {file_path}"

    lines: list[str] = []
    lines.append(f"📂 {_shorten_home(header.cwd)}")
    lines.append(f"🕐 {header.timestamp}")

    user_count = sum(1 for m in messages if m.role == "user")
    lines.append(f"💬 {user_count} messages in session")
    lines.append("")
    lines.append("─" * 50)

    for msg in messages:
        is_target = msg.role == role and msg.index == msg_index
        # For summary entries, highlight the first user message
        if role == "summary" and msg.role == "user" and msg.index == 0:
            is_target = True

        prefix = "▶ YOU" if msg.role == "user" else "◀ PI"
        marker = "  ← ← ←" if is_target else ""

        limit = 800 if is_target else 300
        text = msg.text
        if len(text) > limit:
            text = text[:limit] + "..."

        lines.append("")
        lines.append(f"{prefix}{marker}")
        lines.append(text)

    return "\n".join(lines)
