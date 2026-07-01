# macOS Administration

## Package Management
- Homebrew: `brew install <app>`, `brew search <app>`, `brew list`
- MacPorts: `port install <app>`

## Service Management
- Launchd: `launchctl list`, `launchctl start/stop <service>`
- List all: `sudo launchctl list`

## Process Management
- List: `ps aux`
- Find: `pgrep <name>`
- Kill: `kill <pid>`, `killall <name>`
- Activity: `top -o cpu`

## File System
- Home: `~` = `/Users/<user>`
- Applications: `/Applications`, `~/Applications`
- Library: `~/Library`
- Desktop: `~/Desktop`
- Documents: `~/Documents`
- Downloads: `~/Downloads`

## Common App Paths
- Chrome: `/Applications/Google Chrome.app`
- Safari: `/Applications/Safari.app`
- VS Code: `/Applications/Visual Studio Code.app`
- Terminal: `/Applications/Utilities/Terminal.app`
- Finder: `/System/Library/CoreServices/Finder.app`

## Open Command
- Open app: `open -a "App Name"`
- Open file: `open <file>`
- Open URL: `open <url>`
- Open folder: `open <dir>`

## Network
- IP: `ifconfig`, `ipconfig getifaddr en0`
- DNS: `scutil --dns`
- Ping: `ping <host>`
- Traceroute: `traceroute <host>`

## Disk and Storage
- Usage: `df -h`
- Directory: `du -sh <dir>`

## System Info
- Full: `system_profiler SPSoftwareDataType`
- OS version: `sw_vers`
- Hardware: `system_profiler SPHardwareDataType`

## Text Search
- Spotlight: `mdfind <query>`
- Find: `find / -name "*.txt"`
- Grep: `grep -r "<text>" <dir>`
