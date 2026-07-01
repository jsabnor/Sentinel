# Cross-Platform Reference

## Opening URLs
- Windows: `start <url>`
- Linux: `xdg-open <url>`
- macOS: `open <url>`

## Opening Files with Default App
- Windows: `start <file>`
- Linux: `xdg-open <file>`
- macOS: `open <file>`

## Opening Folders
- Windows: `explorer <dir>`
- Linux: `xdg-open <dir>`
- macOS: `open <dir>`

## Environment Variables
- Windows CMD: `%VAR%`, set with `set VAR=value`
- PowerShell: `$env:VAR`, set with `$env:VAR = "value"`
- Linux/macOS: `$VAR`, set with `export VAR=value`

## Weather and Web APIs
- wttr.in: `curl "wttr.in/City?lang=es&format=%C+%t"`
- Alternative: `curl "wttr.in/City?lang=es"` (full output)
- No API key needed for wttr.in

## File Search
- Windows: `dir /s /b "C:\*.txt"`, `where <pattern>`
- Linux: `find / -name "*.txt"`, `locate <pattern>`
- macOS: `mdfind <query>`, `find / -name "*.txt"`

## Text Search in Files
- Windows: `findstr /s /i "<text>" *.txt`
- Linux: `grep -r "<text>" <dir>`
- macOS: `grep -r "<text>" <dir>`

## Quick Reference: Common Tasks

### Install an application
- Windows: `winget install <app>`
- Linux: `sudo apt install <app>` (Debian) / `sudo dnf install <app>` (RHEL)
- macOS: `brew install <app>`

### Check if app is installed
- Windows: `where <app>` or `winget list <app>`
- Linux: `which <app>` or `dpkg -l | grep <app>`
- macOS: `which <app>` or `brew list | grep <app>`

### Get system resource usage
- Windows: `systeminfo` or task manager data
- Linux: `top -bn1 | head -20`, `free -h`, `df -h`
- macOS: `top -l 1 -n 0`, `vm_stat`

### Kill a frozen application
- Windows: `taskkill /IM <name>.exe /F`
- Linux: `pkill -9 <name>`
- macOS: `killall <name>`

### Check disk space
- Windows: `wmic logicaldisk get size,freespace,caption`
- Linux: `df -h`
- macOS: `df -h`
