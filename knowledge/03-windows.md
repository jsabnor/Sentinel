# Windows Administration

## Package Management
- winget: `winget install <app>`, `winget search <app>`, `winget list`
- chocolatey: `choco install <app>`, `choco list --local-only`
- Manual: download and run installer silently with `/S` or `/quiet`

## Service Management
- List services: `sc query` or `Get-Service`
- Start/stop: `sc start <name>`, `sc stop <name>`, `net start <name>`, `net stop <name>`
- Auto-start: `sc config <name> start=auto`
- Check status: `sc query <name>`

## Process Management
- List: `tasklist`, `Get-Process`
- Kill: `taskkill /PID <pid> /F`, `taskkill /IM <name>.exe /F`
- Find: `tasklist | findstr <name>`

## File System
- User profile: `%USERPROFILE%` = `C:/Users/<name>`
- AppData: `%APPDATA%`, `%LOCALAPPDATA%`
- Program Files: `C:/Program Files`, `C:/Program Files (x86)`
- Temp: `%TEMP%`
- Desktop: `%USERPROFILE%/Desktop`
- Documents: `%USERPROFILE%/Documents`
- Downloads: `%USERPROFILE%/Downloads`

## Common App Paths
- Chrome: `C:/Program Files/Google/Chrome/Application/chrome.exe`
- Firefox: `C:/Program Files/Mozilla Firefox/firefox.exe`
- Edge: `C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe`
- VS Code: `%LOCALAPPDATA%/Programs/Microsoft VS Code/Code.exe`
- Spotify: `%APPDATA%/Spotify/Spotify.exe`
- Notepad: `notepad.exe`
- Calculator: `calc.exe`
- Explorer: `explorer.exe`
- Control Panel: `control`
- Task Manager: `taskmgr.exe`
- Settings: `ms-settings:`

## Network
- IP config: `ipconfig /all`
- DNS flush: `ipconfig /flushdns`
- Ping: `ping <host>`
- Tracert: `tracert <host>`
- Netstat: `netstat -ano`
- Firewall: `netsh advfirewall`

## Disk and Storage
- Disk usage: `wmic logicaldisk get size,freespace,caption`
- Disk info: `Get-PSDrive` or `fsutil volume diskfree C:`
- Check disk: `chkdsk C:`

## System Info
- Full: `systeminfo`
- OS version: `ver`
- Environment: `set`

## User Management
- Current user: `whoami`
- Users list: `net user`
- Groups: `net localgroup`

## Power Management
- Shutdown: `shutdown /s /t 0`
- Restart: `shutdown /r /t 0`
- Sleep: `rundll32.exe powrprof.dll,SetSuspendState Sleep`
- Hibernate: `shutdown /h`

## Registry
- Query: `reg query <key>`
- Get value: `reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /v ProductName`

## Windows-Specific Tips
- Use forward slashes in paths for compatibility: `C:/Users/...`
- Quote paths with spaces: `"C:/Program Files/..."`
- PowerShell is preferred over CMD for complex tasks
- `start "" "path"` to open files/apps non-blocking
- `explorer /select,"path"` to open folder in Explorer
- Path separator is `;` for PATH, `\` for registry
