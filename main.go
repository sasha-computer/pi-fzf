package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strings"
	"time"
)

// sessionHeader is the first line of a Pi session JSONL file.
type sessionHeader struct {
	Type      string `json:"type"`
	Version   int    `json:"version"`
	ID        string `json:"id"`
	Timestamp string `json:"timestamp"`
	Cwd       string `json:"cwd"`
}

// messageEntry is a message line in the JSONL.
type messageEntry struct {
	Type    string  `json:"type"`
	Message message `json:"message"`
}

type message struct {
	Role    string          `json:"role"`
	Content json.RawMessage `json:"content"`
}

// contentBlock is one element in a content array.
type contentBlock struct {
	Type string `json:"type"`
	Text string `json:"text"`
}

// fzfEntry is one line we feed to fzf.
type fzfEntry struct {
	FilePath   string
	MsgIndex   int
	SortKey    string // ISO timestamp for sorting
	DisplayStr string
}

func main() {
	if len(os.Args) > 1 {
		switch os.Args[1] {
		case "preview":
			cmdPreview()
			return
		case "list":
			cmdList()
			return
		case "init":
			cmdInit()
			return
		case "help", "--help", "-h":
			cmdHelp()
			return
		case "version", "--version", "-v":
			fmt.Println("pi-fzf v0.1.0")
			return
		}
	}

	cmdPick()
}

// cmdPick is the default: parse sessions, launch fzf, print result.
func cmdPick() {
	entries := listEntries()
	if len(entries) == 0 {
		fmt.Fprintln(os.Stderr, "No Pi sessions found")
		os.Exit(1)
	}

	self, _ := os.Executable()

	// Build fzf input
	var lines []string
	for _, e := range entries {
		lines = append(lines, fmt.Sprintf("%s\t%d\t%s", e.FilePath, e.MsgIndex, e.DisplayStr))
	}

	fzfArgs := []string{
		"--delimiter", "\t",
		"--with-nth", "3",
		"--preview", fmt.Sprintf("%s preview {1} {2}", self),
		"--preview-window", "right:50%:wrap",
		"--header", "Pi Sessions — search all messages · Enter to resume · Esc to cancel",
		"--prompt", "π › ",
		"--height", "80%",
		"--layout", "reverse",
		"--border", "rounded",
		"--ansi",
	}

	cmd := exec.Command("fzf", fzfArgs...)
	cmd.Stderr = os.Stderr
	cmd.Stdin = strings.NewReader(strings.Join(lines, "\n"))
	out, err := cmd.Output()
	if err != nil {
		// User cancelled (exit 130) or no match (exit 1)
		os.Exit(0)
	}

	selected := strings.TrimSpace(string(out))
	parts := strings.SplitN(selected, "\t", 3)
	if len(parts) < 1 {
		os.Exit(0)
	}

	sessionFile := parts[0]

	// Read the cwd from the session header
	cwd := sessionCwd(sessionFile)

	// Output: session_file\tcwd — the shell wrapper uses this
	fmt.Printf("%s\t%s\n", sessionFile, cwd)
}

// cmdList outputs all entries as TSV (for piping / scripting).
func cmdList() {
	entries := listEntries()
	for _, e := range entries {
		fmt.Printf("%s\t%d\t%s\n", e.FilePath, e.MsgIndex, e.DisplayStr)
	}
}

// cmdPreview renders the full conversation for fzf's preview pane.
func cmdPreview() {
	if len(os.Args) < 4 {
		fmt.Fprintln(os.Stderr, "Usage: pi-fzf preview <file> <msg_index>")
		os.Exit(1)
	}
	filePath := os.Args[2]
	var targetIdx int
	fmt.Sscanf(os.Args[3], "%d", &targetIdx)

	home, _ := os.UserHomeDir()

	f, err := os.Open(filePath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Cannot open %s: %v\n", filePath, err)
		os.Exit(1)
	}
	defer f.Close()

	scanner := bufio.NewScanner(f)
	scanner.Buffer(make([]byte, 0, 1024*1024), 10*1024*1024)

	// Read header
	var header sessionHeader
	if scanner.Scan() {
		json.Unmarshal(scanner.Bytes(), &header)
	}

	shortCwd := strings.Replace(header.Cwd, home, "~", 1)
	fmt.Printf("📂 %s\n", shortCwd)
	fmt.Printf("🕐 %s\n", header.Timestamp)

	// Collect messages
	type msg struct {
		Role     string
		Text     string
		IsTarget bool
	}
	var messages []msg
	userIdx := 0

	// Reset and re-scan
	f.Seek(0, 0)
	scanner = bufio.NewScanner(f)
	scanner.Buffer(make([]byte, 0, 1024*1024), 10*1024*1024)

	for scanner.Scan() {
		var entry messageEntry
		if err := json.Unmarshal(scanner.Bytes(), &entry); err != nil {
			continue
		}
		if entry.Type != "message" {
			continue
		}
		role := entry.Message.Role
		if role != "user" && role != "assistant" {
			continue
		}

		text := extractText(entry.Message.Content)
		if text == "" {
			if role == "user" {
				userIdx++
			}
			continue
		}

		isTarget := role == "user" && userIdx == targetIdx
		messages = append(messages, msg{Role: role, Text: text, IsTarget: isTarget})
		if role == "user" {
			userIdx++
		}
	}

	totalUser := 0
	for _, m := range messages {
		if m.Role == "user" {
			totalUser++
		}
	}
	fmt.Printf("💬 %d messages in session\n", totalUser)
	fmt.Println()
	fmt.Println("────────────────────────────────────────────────────────────")

	for _, m := range messages {
		prefix := "◀ PI"
		if m.Role == "user" {
			prefix = "▶ YOU"
		}
		marker := ""
		if m.IsTarget {
			marker = "  ← ← ←"
		}
		fmt.Println()
		fmt.Printf("%s%s\n", prefix, marker)

		limit := 300
		if m.IsTarget {
			limit = 800
		}
		t := m.Text
		if len(t) > limit {
			t = t[:limit] + "..."
		}
		fmt.Println(t)
	}
}

// cmdInit outputs shell integration code.
func cmdInit() {
	if len(os.Args) < 3 {
		fmt.Println("Usage: pi-fzf init <fish|bash|zsh>")
		os.Exit(1)
	}
	switch os.Args[2] {
	case "fish":
		fmt.Print(fishInit)
	case "bash":
		fmt.Print(bashInit)
	case "zsh":
		fmt.Print(zshInit)
	default:
		fmt.Fprintf(os.Stderr, "Unknown shell: %s (supported: fish, bash, zsh)\n", os.Args[2])
		os.Exit(1)
	}
}

func cmdHelp() {
	fmt.Print(`pi-fzf — fuzzy find and resume Pi coding agent sessions

Usage:
  pi-fzf              Launch the fuzzy finder (default)
  pi-fzf list         List all entries as TSV
  pi-fzf preview F N  Show session preview (used by fzf)
  pi-fzf init SHELL   Output shell integration (fish, bash, zsh)
  pi-fzf version      Print version
  pi-fzf help         Show this help

Shortcuts:
  Alt+P                    Launch picker (after shell init)

Requires:
  fzf                      https://github.com/junegunn/fzf
  pi                       https://github.com/badlogic/pi-mono
`)
}

// --- Session parsing ---

func sessionsDir() string {
	if dir := os.Getenv("PI_CODING_AGENT_DIR"); dir != "" {
		return filepath.Join(dir, "sessions")
	}
	home, _ := os.UserHomeDir()
	return filepath.Join(home, ".pi", "agent", "sessions")
}

func listEntries() []fzfEntry {
	home, _ := os.UserHomeDir()
	root := sessionsDir()

	var entries []fzfEntry

	filepath.Walk(root, func(path string, info os.FileInfo, err error) error {
		if err != nil || info.IsDir() || !strings.HasSuffix(path, ".jsonl") {
			return nil
		}

		f, err := os.Open(path)
		if err != nil {
			return nil
		}
		defer f.Close()

		scanner := bufio.NewScanner(f)
		scanner.Buffer(make([]byte, 0, 1024*1024), 10*1024*1024)

		// Parse header
		if !scanner.Scan() {
			return nil
		}
		var header sessionHeader
		if err := json.Unmarshal(scanner.Bytes(), &header); err != nil || header.Type != "session" {
			return nil
		}

		shortCwd := strings.Replace(header.Cwd, home, "~", 1)

		// Format timestamp
		niceTs := header.Timestamp[:16]
		sortTs := header.Timestamp
		if t, err := time.Parse(time.RFC3339Nano, header.Timestamp); err == nil {
			niceTs = t.Format("Jan 02 15:04")
			sortTs = t.Format(time.RFC3339Nano)
		} else if t, err := time.Parse("2006-01-02T15:04:05.000Z", header.Timestamp); err == nil {
			niceTs = t.Format("Jan 02 15:04")
			sortTs = t.Format(time.RFC3339Nano)
		}

		// Scan for user messages
		msgIdx := 0
		for scanner.Scan() {
			var entry messageEntry
			if err := json.Unmarshal(scanner.Bytes(), &entry); err != nil {
				continue
			}
			if entry.Type != "message" || entry.Message.Role != "user" {
				continue
			}

			text := extractText(entry.Message.Content)
			if text == "" {
				msgIdx++
				continue
			}

			// Flatten to single line, truncate
			text = strings.Join(strings.Fields(text), " ")
			if len(text) > 200 {
				text = text[:200]
			}

			display := fmt.Sprintf("%s  %s  │  %s", niceTs, shortCwd, text)
			entries = append(entries, fzfEntry{
				FilePath:   path,
				MsgIndex:   msgIdx,
				SortKey:    sortTs,
				DisplayStr: display,
			})
			msgIdx++
		}

		return nil
	})

	// Sort newest first, then by message index descending (latest messages first)
	sort.Slice(entries, func(i, j int) bool {
		if entries[i].SortKey != entries[j].SortKey {
			return entries[i].SortKey > entries[j].SortKey
		}
		return entries[i].MsgIndex > entries[j].MsgIndex
	})

	return entries
}

func extractText(raw json.RawMessage) string {
	// Try as string first
	var s string
	if err := json.Unmarshal(raw, &s); err == nil {
		return strings.TrimSpace(s)
	}

	// Try as array of content blocks
	var blocks []contentBlock
	if err := json.Unmarshal(raw, &blocks); err == nil {
		for _, b := range blocks {
			if b.Type == "text" && strings.TrimSpace(b.Text) != "" {
				return strings.TrimSpace(b.Text)
			}
		}
	}

	return ""
}

func sessionCwd(path string) string {
	f, err := os.Open(path)
	if err != nil {
		return ""
	}
	defer f.Close()
	scanner := bufio.NewScanner(f)
	scanner.Buffer(make([]byte, 0, 64*1024), 1024*1024)
	if scanner.Scan() {
		var h sessionHeader
		json.Unmarshal(scanner.Bytes(), &h)
		return h.Cwd
	}
	return ""
}

// --- Shell integration ---

const fishInit = `# Pi Sessions — shell integration for fish
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

bind \ep pi-fzf-widget
`

const bashInit = `# Pi Sessions — shell integration for bash
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

bind -x '"\ep": pi-fzf-widget'
`

const zshInit = `# Pi Sessions — shell integration for zsh
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
bindkey '\ep' pi-fzf-widget
`
