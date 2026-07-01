# Linux Administration

## Package Management
- Debian/Ubuntu: `apt`, `apt-get`, `dpkg`
- RHEL/Fedora: `dnf`, `yum`, `rpm`
- Arch: `pacman`, `yay`
- SUSE: `zypper`
- Flatpak: `flatpak`
- Snap: `snap`

Common: `sudo apt update && sudo apt install <pkg>`, `sudo dnf install <pkg>`

## Service Management (systemd)
- List: `systemctl list-units --type=service`
- Start/stop: `sudo systemctl start/stop <service>`
- Enable/disable: `sudo systemctl enable/disable <service>`
- Status: `systemctl status <service>`
- Journal: `journalctl -u <service>`

## Process Management
- List: `ps aux`, `top -bn1`, `htop`
- Find: `pgrep <name>`, `ps aux | grep <name>`
- Kill: `kill <pid>`, `killall <name>`, `pkill <name>`
- Force: `kill -9 <pid>`

## File System
- Home: `~` = `/home/<user>`
- Root: `/`
- Config: `/etc`
- Logs: `/var/log`
- Temp: `/tmp`
- Binaries: `/usr/bin`, `/usr/local/bin`
- Desktop/Documents/Downloads: `~/Desktop`, `~/Documents`, `~/Downloads`

## Common App Paths
- Chrome: `google-chrome`, `google-chrome-stable`
- Firefox: `firefox`
- VS Code: `code`
- Terminal: `gnome-terminal`, `konsole`, `xterm`
- Files: `nautilus`, `dolphin`, `thunar`

## Opening URLs/Files
- `xdg-open <url>` — open URL in default browser
- `xdg-open <file>` — open file with default app
- `xdg-open <dir>` — open folder in file manager

## Network
- IP: `ip addr`, `ifconfig`
- DNS: `cat /etc/resolv.conf`
- Ping: `ping <host>`
- Traceroute: `traceroute <host>`
- Netstat: `ss -tuln`
- Firewall: `sudo ufw status`, `sudo iptables -L`
- Download: `wget <url>`, `curl -O <url>`

## Disk and Storage
- Usage: `df -h`
- Directory size: `du -sh <dir>`
- Mounts: `mount`, `lsblk`
- Free memory: `free -h`

## System Info
- Full: `uname -a`, `hostnamectl`
- CPU: `lscpu`, `cat /proc/cpuinfo`
- Memory: `cat /proc/meminfo`
- Distro: `cat /etc/os-release`, `lsb_release -a`

## User Management
- Current: `whoami`, `id`
- Users: `cat /etc/passwd`
- Groups: `groups`, `cat /etc/group`
- Add user: `sudo useradd <name>`
- Sudo: `sudo <command>`

## Power
- Shutdown: `sudo shutdown now`
- Restart: `sudo reboot`
- Suspend: `sudo systemctl suspend`

## Text Search
- `grep -r "<text>" <directory>`
- `find / -name "*.txt"`
- `locate <pattern>`
