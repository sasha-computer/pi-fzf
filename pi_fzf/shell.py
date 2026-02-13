"""Shell integration init strings for fish, bash, and zsh."""

FISH_INIT = """\
# Pi Sessions — shell integration for fish
# Add to ~/.config/fish/config.fish:
#   pi-fzf init fish | source

function pi-fzf-widget --description "Fuzzy find and resume a Pi session"
    set -l result (pi-fzf 2>/dev/null)
    if test -z "$result"
        commandline -f repaint
        return
    end

    set -l session_file (echo "$result" | cut -f1)
    set -l target_cwd (echo "$result" | cut -f2)

    if test -n "$target_cwd" -a -d "$target_cwd"
        cd "$target_cwd"
    end

    commandline "pi --session $session_file"
    commandline -f execute
end

bind \\ep pi-fzf-widget
"""

BASH_INIT = """\
# Pi Sessions — shell integration for bash
# Add to ~/.bashrc:
#   eval "$(pi-fzf init bash)"

pi-fzf-widget() {
    local result
    result=$(pi-fzf 2>/dev/null)
    [[ -z "$result" ]] && return

    local session_file target_cwd
    session_file=$(echo "$result" | cut -f1)
    target_cwd=$(echo "$result" | cut -f2)

    [[ -n "$target_cwd" && -d "$target_cwd" ]] && cd "$target_cwd"
    READLINE_LINE="pi --session $session_file"
    READLINE_POINT=${#READLINE_LINE}
}

bind -x '"\\ep": pi-fzf-widget'
"""

ZSH_INIT = """\
# Pi Sessions — shell integration for zsh
# Add to ~/.zshrc:
#   eval "$(pi-fzf init zsh)"

pi-fzf-widget() {
    local result
    result=$(pi-fzf 2>/dev/null)
    [[ -z "$result" ]] && return

    local session_file target_cwd
    session_file=$(echo "$result" | cut -f1)
    target_cwd=$(echo "$result" | cut -f2)

    [[ -n "$target_cwd" && -d "$target_cwd" ]] && cd "$target_cwd"
    BUFFER="pi --session $session_file"
    CURSOR=${#BUFFER}
    zle accept-line
}

zle -N pi-fzf-widget
bindkey '\\ep' pi-fzf-widget
"""

SHELLS = {
    "fish": FISH_INIT,
    "bash": BASH_INIT,
    "zsh": ZSH_INIT,
}
