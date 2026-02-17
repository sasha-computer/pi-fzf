"""CLI entry point for pi-chat-fzf."""

from __future__ import annotations

import subprocess
import sys

from pi_chat_fzf.index import list_entries
from pi_chat_fzf.preview import render_preview
from pi_chat_fzf.sessions import session_cwd
from pi_chat_fzf.shell import SHELLS

VERSION = "0.2.0"


def cmd_pick() -> None:
    """Default command: parse sessions, launch fzf, print result."""
    entries = list_entries()
    if not entries:
        print("No Pi sessions found", file=sys.stderr)
        sys.exit(1)

    self_cmd = sys.argv[0]

    # Build fzf input: file_path\trole\tmsg_index\tdisplay
    lines = [f"{e.file_path}\t{e.role}\t{e.msg_index}\t{e.display}" for e in entries]

    fzf_args = [
        "fzf",
        "--delimiter",
        "\t",
        "--with-nth",
        "4",
        "--preview",
        f"{self_cmd} preview {{1}} {{2}} {{3}}",
        "--preview-window",
        "right:50%:wrap",
        "--header",
        "Pi Sessions — search all messages · Enter to resume · Esc to cancel",
        "--prompt",
        "π › ",
        "--height",
        "80%",
        "--layout",
        "reverse",
        "--border",
        "rounded",
        "--ansi",
    ]

    try:
        result = subprocess.run(
            fzf_args,
            input="\n".join(lines),
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        print("fzf not found — install it: https://github.com/junegunn/fzf", file=sys.stderr)
        sys.exit(1)

    if result.returncode != 0:
        sys.exit(0)

    selected = result.stdout.strip()
    parts = selected.split("\t", 3)
    if not parts:
        sys.exit(0)

    session_file = parts[0]
    from pathlib import Path

    cwd = session_cwd(Path(session_file))
    print(f"{session_file}\t{cwd}")


def cmd_list() -> None:
    """Output all entries as TSV."""
    for e in list_entries():
        print(f"{e.file_path}\t{e.role}\t{e.msg_index}\t{e.display}")


def cmd_preview() -> None:
    """Render conversation preview for fzf's preview pane."""
    if len(sys.argv) < 5:
        print("Usage: pi-chat-fzf preview <file> <role> <msg_index>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[2]
    role = sys.argv[3]
    try:
        msg_index = int(sys.argv[4])
    except ValueError:
        msg_index = 0

    print(render_preview(file_path, role, msg_index))


def cmd_init() -> None:
    """Output shell integration code."""
    if len(sys.argv) < 3:
        print("Usage: pi-chat-fzf init <fish|bash|zsh>", file=sys.stderr)
        sys.exit(1)

    shell = sys.argv[2]
    if shell not in SHELLS:
        print(f"Unknown shell: {shell} (supported: fish, bash, zsh)", file=sys.stderr)
        sys.exit(1)

    print(SHELLS[shell], end="")


def cmd_help() -> None:
    """Show help."""
    print("""\
pi-chat-fzf — fuzzy find and resume Pi coding agent sessions

Usage:
  pi-chat-fzf                    Launch the fuzzy finder (default)
  pi-chat-fzf list               List all entries as TSV
  pi-chat-fzf preview F R N      Show session preview (used by fzf)
  pi-chat-fzf init SHELL         Output shell integration (fish, bash, zsh)
  pi-chat-fzf version            Print version
  pi-chat-fzf help               Show this help

Shortcuts:
  Alt+P                     Launch picker (after shell init)

Requires:
  fzf                       https://github.com/junegunn/fzf
  pi                        https://github.com/badlogic/pi-mono""")


def main() -> None:
    """Entry point."""
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        match cmd:
            case "preview":
                cmd_preview()
            case "list":
                cmd_list()
            case "init":
                cmd_init()
            case "help" | "--help" | "-h":
                cmd_help()
            case "version" | "--version" | "-v":
                print(f"pi-chat-fzf v{VERSION}")
            case _:
                cmd_pick()
    else:
        cmd_pick()


if __name__ == "__main__":
    main()
