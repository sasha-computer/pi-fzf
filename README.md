<p align="center">
  <img src="demo.gif" alt="pi-sessions demo" width="800" />
</p>

# pi-sessions

Fuzzy find and resume [Pi](https://github.com/badlogic/pi-mono) coding agent sessions. Searches across **every user message** in every session, so you can find that thing you worked on three days ago by typing a few words.

## Install

### Go

```bash
go install github.com/sasha-computer/pi-sessions@latest
```

### From source

```bash
git clone https://github.com/sasha-computer/pi-sessions.git
cd pi-sessions
go build -o pi-sessions .
# Move to somewhere on your PATH
mv pi-sessions /usr/local/bin/
```

## Shell Integration

### Fish

```fish
# ~/.config/fish/config.fish
pi-sessions init fish | source
```

### Bash

```bash
# ~/.bashrc
eval "$(pi-sessions init bash)"
```

### Zsh

```zsh
# ~/.zshrc
eval "$(pi-sessions init zsh)"
```

All shells bind **Alt+P** to launch the picker.

## Usage

Launch directly:

```bash
pi-sessions
```

Or press **Alt+P** in your shell (after adding the init above). The picker shows every message you've sent to Pi across all sessions:

- **Type** to fuzzy search across all messages
- **↑/↓** to navigate
- **Enter** to `cd` into the session's directory and resume it
- **Esc** to cancel

The preview pane shows the full conversation with your selected message highlighted.

### Commands

| Command | Description |
|---------|-------------|
| `pi-sessions` | Launch the fuzzy finder (default) |
| `pi-sessions list` | List all entries as TSV (for piping) |
| `pi-sessions init <shell>` | Output shell integration (`fish`, `bash`, `zsh`) |
| `pi-sessions help` | Show help |
| `pi-sessions version` | Print version |

## How It Works

Pi stores sessions as JSONL files in `~/.pi/agent/sessions/`. Each file contains a session header (with the working directory and timestamp) followed by message entries.

`pi-sessions` walks all session files, extracts every user message, and pipes them to [fzf](https://github.com/junegunn/fzf) for fuzzy searching. When you select a message, it resumes the session with `pi --session <file>`.

No database, no indexing, no background process. Just fast file parsing (~300ms for hundreds of sessions) and fzf.

## Requirements

- [fzf](https://github.com/junegunn/fzf)
- [Pi](https://github.com/badlogic/pi-mono)

## License

MIT
