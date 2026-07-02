# Opening Applications

When asked to open an application, follow this exact flow:

## Step 1: Find the App
Use NORMAL commands to locate the executable. Do NOT add "start" prefix.
- `where spotify` — check if it's in PATH
- `dir /s /b "C:\Program Files\Spotify\Spotify.exe"` — search common locations
- `dir "%LOCALAPPDATA%\Spotify"` — check local app data
- `winget list spotify` — check if installed via winget

These are SEARCH commands. The system runs them normally (blocking).

## Step 2: Launch the App
Use the direct executable path. The system automatically handles non-blocking launch.
- Just pass the path: `"C:/Users/josem/AppData/Roaming/Spotify/Spotify.exe"`
- No need to add "start" — the system does it automatically.
- Use timeout=3. The launch returns immediately.

## Step 3: Verify
- Wait 2 seconds
- Call window_list ONCE
- If the window is there, respond: "He abierto Spotify"
- If not visible yet: "Spotify se esta abriendo, puede tardar unos segundos"

## Step 4: Stop
- You are DONE. Do NOT:
  - Add "start" prefix to search/find commands
  - Keep checking window_list repeatedly
  - Try alternative launch methods
  - Re-open if the user closes it
  - Monitor or watch applications

## Important: Match App to Request
- "Play music" / "reproduce X" / "pon X" → Spotify or media player, NOT browser
- "Search the web" / "busca X" → browser (Edge/Chrome)
- "Open YouTube" → browser to youtube.com
- "Play X on Spotify" → find Spotify.exe, launch it, then trust Spotify to handle search. Do NOT open browser.
- If user says "Spotify", ALWAYS use Spotify, never fallback to YouTube or browser.
