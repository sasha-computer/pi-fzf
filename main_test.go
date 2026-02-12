package main

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestExtractText_String(t *testing.T) {
	raw := json.RawMessage(`"hello world"`)
	got := extractText(raw)
	if got != "hello world" {
		t.Errorf("extractText(string) = %q, want %q", got, "hello world")
	}
}

func TestExtractText_StringWithWhitespace(t *testing.T) {
	raw := json.RawMessage(`"  trimmed  "`)
	got := extractText(raw)
	if got != "trimmed" {
		t.Errorf("extractText(whitespace string) = %q, want %q", got, "trimmed")
	}
}

func TestExtractText_ContentBlocks(t *testing.T) {
	raw := json.RawMessage(`[{"type":"text","text":"block content"}]`)
	got := extractText(raw)
	if got != "block content" {
		t.Errorf("extractText(blocks) = %q, want %q", got, "block content")
	}
}

func TestExtractText_ContentBlocksSkipsNonText(t *testing.T) {
	raw := json.RawMessage(`[{"type":"image","data":"abc"},{"type":"text","text":"found it"}]`)
	got := extractText(raw)
	if got != "found it" {
		t.Errorf("extractText(mixed blocks) = %q, want %q", got, "found it")
	}
}

func TestExtractText_EmptyBlocks(t *testing.T) {
	raw := json.RawMessage(`[{"type":"image","data":"abc"}]`)
	got := extractText(raw)
	if got != "" {
		t.Errorf("extractText(no text blocks) = %q, want %q", got, "")
	}
}

func TestExtractText_EmptyString(t *testing.T) {
	raw := json.RawMessage(`""`)
	got := extractText(raw)
	if got != "" {
		t.Errorf("extractText(empty string) = %q, want %q", got, "")
	}
}

func TestExtractText_Invalid(t *testing.T) {
	raw := json.RawMessage(`{invalid}`)
	got := extractText(raw)
	if got != "" {
		t.Errorf("extractText(invalid) = %q, want %q", got, "")
	}
}

func TestSessionCwd(t *testing.T) {
	cwd := sessionCwd("testdata/valid_session.jsonl")
	want := "/Users/test/projects/myapp"
	if cwd != want {
		t.Errorf("sessionCwd() = %q, want %q", cwd, want)
	}
}

func TestSessionCwd_NonexistentFile(t *testing.T) {
	cwd := sessionCwd("testdata/nonexistent.jsonl")
	if cwd != "" {
		t.Errorf("sessionCwd(nonexistent) = %q, want empty", cwd)
	}
}

func TestListEntries_ValidSession(t *testing.T) {
	// Point sessionsDir to our testdata
	abs, _ := filepath.Abs("testdata")
	t.Setenv("PI_CODING_AGENT_DIR", abs)

	// Create the expected structure: PI_CODING_AGENT_DIR/sessions/
	sessDir := filepath.Join(abs, "sessions")
	os.MkdirAll(sessDir, 0755)
	defer os.RemoveAll(sessDir)

	// Copy test fixture into sessions dir
	data, _ := os.ReadFile("testdata/valid_session.jsonl")
	os.WriteFile(filepath.Join(sessDir, "valid_session.jsonl"), data, 0644)

	entries := listEntries()
	if len(entries) != 3 {
		t.Fatalf("listEntries() returned %d entries, want 3", len(entries))
	}

	// Entries are sorted newest-first, and within a session by msg index descending
	// So msg index 2 ("Deploy to staging") should come first
	if entries[0].MsgIndex != 2 {
		t.Errorf("first entry MsgIndex = %d, want 2", entries[0].MsgIndex)
	}
	if !strings.Contains(entries[0].DisplayStr, "Deploy to staging") {
		t.Errorf("first entry display = %q, should contain 'Deploy to staging'", entries[0].DisplayStr)
	}
	if !strings.Contains(entries[1].DisplayStr, "Now add rate limiting") {
		t.Errorf("second entry display = %q, should contain 'Now add rate limiting'", entries[1].DisplayStr)
	}
	if !strings.Contains(entries[2].DisplayStr, "Fix the login bug") {
		t.Errorf("third entry display = %q, should contain 'Fix the login bug'", entries[2].DisplayStr)
	}
}

func TestListEntries_EmptySession(t *testing.T) {
	abs, _ := filepath.Abs("testdata")
	t.Setenv("PI_CODING_AGENT_DIR", abs)

	sessDir := filepath.Join(abs, "sessions")
	os.MkdirAll(sessDir, 0755)
	defer os.RemoveAll(sessDir)

	data, _ := os.ReadFile("testdata/empty_session.jsonl")
	os.WriteFile(filepath.Join(sessDir, "empty_session.jsonl"), data, 0644)

	entries := listEntries()
	if len(entries) != 0 {
		t.Errorf("listEntries(empty session) returned %d entries, want 0", len(entries))
	}
}

func TestListEntries_NoTextContent(t *testing.T) {
	abs, _ := filepath.Abs("testdata")
	t.Setenv("PI_CODING_AGENT_DIR", abs)

	sessDir := filepath.Join(abs, "sessions")
	os.MkdirAll(sessDir, 0755)
	defer os.RemoveAll(sessDir)

	data, _ := os.ReadFile("testdata/no_text_content.jsonl")
	os.WriteFile(filepath.Join(sessDir, "no_text_content.jsonl"), data, 0644)

	entries := listEntries()
	if len(entries) != 0 {
		t.Errorf("listEntries(no text) returned %d entries, want 0", len(entries))
	}
}

func TestListEntries_MultipleSessionsSorted(t *testing.T) {
	abs, _ := filepath.Abs("testdata")
	t.Setenv("PI_CODING_AGENT_DIR", abs)

	sessDir := filepath.Join(abs, "sessions")
	os.MkdirAll(sessDir, 0755)
	defer os.RemoveAll(sessDir)

	// Copy both sessions — multi_session is newer (Dec 5) than valid_session (Dec 1)
	for _, name := range []string{"valid_session.jsonl", "multi_session.jsonl"} {
		data, _ := os.ReadFile(filepath.Join("testdata", name))
		os.WriteFile(filepath.Join(sessDir, name), data, 0644)
	}

	entries := listEntries()
	if len(entries) != 5 {
		t.Fatalf("listEntries(multi) returned %d entries, want 5", len(entries))
	}

	// The newer session (Dec 5, multi_session) should come first
	if !strings.Contains(entries[0].DisplayStr, "Add migration scripts") &&
		!strings.Contains(entries[0].DisplayStr, "Set up the database schema") {
		t.Errorf("first entry should be from the newer session, got: %s", entries[0].DisplayStr)
	}
}

func TestListEntries_NoSessions(t *testing.T) {
	tmp := t.TempDir()
	t.Setenv("PI_CODING_AGENT_DIR", tmp)

	// No sessions dir at all
	entries := listEntries()
	if len(entries) != 0 {
		t.Errorf("listEntries(no dir) returned %d entries, want 0", len(entries))
	}
}

func TestShellInit_Fish(t *testing.T) {
	if !strings.Contains(fishInit, "pi-fzf-widget") {
		t.Error("fish init should contain pi-fzf-widget function")
	}
	if !strings.Contains(fishInit, `bind \ep`) {
		t.Error("fish init should bind Alt+P")
	}
}

func TestShellInit_Bash(t *testing.T) {
	if !strings.Contains(bashInit, "pi-fzf-widget") {
		t.Error("bash init should contain pi-fzf-widget function")
	}
	if !strings.Contains(bashInit, `bind -x`) {
		t.Error("bash init should use bind -x")
	}
}

func TestShellInit_Zsh(t *testing.T) {
	if !strings.Contains(zshInit, "pi-fzf-widget") {
		t.Error("zsh init should contain pi-fzf-widget function")
	}
	if !strings.Contains(zshInit, `bindkey`) {
		t.Error("zsh init should use bindkey")
	}
}
