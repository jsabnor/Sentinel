# Efficient Command Patterns

## Golden Rules for Tool Usage
- Combine searches: use `||` or `&&` to chain commands instead of separate calls.
- One tool call = one round trip. Minimize round trips.
- If a command fails, try ONE alternative, then report. Don't keep guessing.

## Finding and Opening Apps (Windows)
Combine search and launch in minimal steps:

```
# Step 1: Find the EXE (ONE command combining multiple paths)
dir /s /b "C:\Program Files\Chrome\chrome.exe" "C:\Program Files (x86)\Edge\msedge.exe" "C:\Program Files\Mozilla Firefox\firefox.exe" 2>nul

# Step 2: Launch what you found (ONE command)
"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" "https://..."
```

Never do: `where chrome` → `where msedge` → `where firefox` → `dir ... chrome` → `dir ... edge`. That's 5 calls. Do it in 1-2.

## Opening URLs
Just pass the URL directly — the system opens the default browser:
```
"https://www.youtube.com"
-or-
start "" "https://www.youtube.com"
```

## Weather and Web APIs
Use ONE curl command with a good format:
```
curl -s "wttr.in/City?lang=es&format=%C+%t+%w+%h" 2>nul
```

Don't try multiple curl calls with different formats. If the first fails, try the full output.

## System Information
Get everything in one call:
```
systeminfo | findstr /C:"OS" /C:"Memory" /C:"Processor"
```

## Maximum Tool Calls Per Request
- Simple tasks (open app, check weather): 1-2 calls
- Medium tasks (install + open app): 3-4 calls  
- Complex tasks (diagnose + fix): 5-6 calls
- If you need more than 6 calls, simplify your approach or ask the user

## If You Get Stuck
- After 2 failed attempts with the same tool, try a DIFFERENT approach
- If 3 different approaches fail, tell the user what you tried and ask for guidance
- Don't loop. Don't retry the same failing command.
