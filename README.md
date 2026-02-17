<p align="center">
  <img src="assets/hero.png" alt="pi-chat-fzf" width="200" />
</p>

<h1 align="center">pi-chat-fzf</h1>

<p align="center">
  Fuzzy find and resume <a href="https://github.com/badlogic/pi-mono">Pi</a> coding agent sessions from any terminal.
</p>

<p align="center">
  <a href="#why">Why</a> ·
  <a href="#how-it-works">How it works</a> ·
  <a href="#installation">Installation</a> ·
  <a href="#shell-integration">Shell integration</a> ·
  <a href="#usage">Usage</a>
</p>

## Why

You've been using Pi for weeks. Dozens of sessions across different projects. You remember working on that DNS thing three days ago but can't remember which session it was. Or you want to pick up where you left off on that refactor but the session file is buried in `~/.pi/agent/sessions/` with a UUID name.

**pi-chat-fzf fixes this.** It indexes every message — yours and Pi's — across all sessions and drops you into fzf. Type a few words you remember, hit enter, and you're back in that session, in the right directory.

## How it works

<p align="center">
  <img src="demo.gif" alt="pi-chat-fzf demo" width="800" />
</p>

- Indexes all user and assistant messages from every Pi session
- Session summary lines (📋 3 msgs · Fix the login bug...) give you an overview without expanding
- Preview pane shows the full conversation with your selected message highlighted
- Selecting a session `cd`s to its working directory and resumes it with `pi --session`
- No database, no background process — just fast JSONL parsing

## Installation

```bash
# With uv (recommended)
uv tool install git+https://github.com/sasha-computer/pi-chat-fzf.git

# From source
git clone https://github.com/sasha-computer/pi-chat-fzf.git
cd pi-chat-fzf
uv tool install .
```

Requires [fzf](https://github.com/junegunn/fzf) and [Pi](https://github.com/badlogic/pi-mono).

## Shell integration

Add one line to your shell config to get **Alt+P** as a keybinding:

### Fish

```fish
# ~/.config/fish/config.fish
pi-chat-fzf init fish | source
```

### Bash

```bash
# ~/.bashrc
eval "$(pi-chat-fzf init bash)"
```

### Zsh

```zsh
# ~/.zshrc
eval "$(pi-chat-fzf init zsh)"
```

This registers a widget bound to **Alt+P** that launches the picker, `cd`s into the session's directory, and resumes it — all inline in your shell.

> Alt+P works in standalone terminals but may be swallowed by multiplexers like Zellij or tmux. You can always run `pi-chat-fzf` directly instead.

## Usage

```bash
pi-chat-fzf              # launch the picker
pi-chat-fzf list         # dump all entries as TSV (for piping)
pi-chat-fzf init SHELL   # output shell integration (fish, bash, zsh)
pi-chat-fzf version      # print version
pi-chat-fzf help         # show help
```

In the picker:

- **Type** to fuzzy search across all messages
- **↑/↓** to navigate
- **Enter** to resume the selected session
- **Esc** to cancel

## License

MIT
