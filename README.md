<p align="center">
  <img src="demo.gif" alt="pi-fzf demo" width="800" />
</p>

# pi-fzf

Fuzzy find and resume [Pi](https://github.com/badlogic/pi-mono) coding agent sessions. Indexes **every message you've sent** across every session — not the AI's responses, just yours — so you can find that thing you worked on three days ago by typing a few words you remember saying.

## Install

### Go

```bash
go install github.com/sasha-computer/pi-fzf@latest
```

### From source

```bash
git clone https://github.com/sasha-computer/pi-fzf.git
cd pi-fzf
go build -o pi-fzf .
# Move to somewhere on your PATH
mv pi-fzf /usr/local/bin/
```

## Shell Integration

### Fish

```fish
# ~/.config/fish/config.fish
pi-fzf init fish | source
```

### Bash

```bash
# ~/.bashrc
eval "$(pi-fzf init bash)"
```

### Zsh

```zsh
# ~/.zshrc
eval "$(pi-fzf init zsh)"
```

Each shell integration registers a **widget function** (e.g. `pi-fzf-widget` in fish) and binds it to **Alt+P**. The widget launches the picker, and when you select a session it `cd`s into the session's original working directory and runs `pi --session <file>` — all inline in your shell, no extra terminal needed.

> **Note:** Alt+P works in a standalone terminal but may be swallowed by terminal multiplexers like Zellij or tmux. You can always run `pi-fzf` directly as a command instead.

## Usage

Launch directly:

```bash
pi-fzf
```

Or press **Alt+P** in your shell (after adding the init above).

Every message you've ever sent to Pi is searchable — across all sessions, all projects. The list shows your message text alongside the session's directory and timestamp, so you can tell sessions apart at a glance.

- **Type** to fuzzy search across all your messages
- **↑/↓** to navigate
- **Enter** to `cd` into the session's directory and resume it
- **Esc** to cancel

The preview pane shows the full conversation (both your messages and Pi's responses) with your selected message highlighted with `← ← ←`.

### Commands

| Command | Description |
|---------|-------------|
| `pi-fzf` | Launch the fuzzy finder (default) |
| `pi-fzf list` | List all entries as TSV (for piping) |
| `pi-fzf init <shell>` | Output shell integration (`fish`, `bash`, `zsh`) |
| `pi-fzf help` | Show help |
| `pi-fzf version` | Print version |

## How It Works

Pi stores sessions as JSONL files in `~/.pi/agent/sessions/`. Each file contains a session header (with the working directory and timestamp) followed by message entries.

`pi-fzf` walks all session files and extracts every message you sent (not the AI's responses — just yours). Each message becomes one line in fzf, so you're fuzzy searching across everything you've ever said to Pi. When you select a message, it resumes that session with `pi --session <file>`.

No database, no indexing, no background process. Just fast JSONL parsing (~300ms for hundreds of sessions and thousands of messages) and fzf.

## Requirements

- [fzf](https://github.com/junegunn/fzf)
- [Pi](https://github.com/badlogic/pi-mono)

## License

MIT
