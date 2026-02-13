# demo.tape
Output demo.mp4
Output demo.gif

Set Shell "fish"
Set Width 1100
Set Height 620
Set FontSize 20
Set FontFamily "Berkeley Mono Variable"
Set Padding 24
Set Theme "Catppuccin Frappe"
Set TypingSpeed 40ms
Set Framerate 30

Hide
Type "clear"
Enter
Sleep 1000ms
Show

Sleep 800ms

Type "pi-fzf"
Sleep 600ms
Enter
Sleep 3000ms

# Search for something
Type "bookmarks"
Sleep 3000ms

# Move down a couple entries
Down
Sleep 1500ms
Down
Sleep 1500ms

# Clear search and try another
Ctrl+U
Sleep 800ms
Type "todoist"
Sleep 3000ms

# Cancel out
Escape
Sleep 1500ms

Sleep 2000ms
