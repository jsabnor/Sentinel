#!/bin/bash
# Sentinel - Linux/macOS Service Installer
# Installs Sentinel as a background service.
# Usage: bash install_service.sh [install|uninstall]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="$(which python3 || which python)"

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

detect_os() {
    case "$(uname -s)" in
        Linux*)     echo "linux" ;;
        Darwin*)    echo "macos" ;;
        *)          echo "unknown" ;;
    esac
}

OS=$(detect_os)
ACTION="${1:-install}"

echo -e "${CYAN}=== Sentinel Service Installer (${OS}) ===${NC}"
echo ""
echo "Project: $SCRIPT_DIR"
echo "Python:  $PYTHON"
echo "OS:      $OS"
echo ""

if [ "$OS" = "unknown" ]; then
    echo -e "${RED}Unsupported operating system.${NC}"
    exit 1
fi

if [ ! -f "$PYTHON" ]; then
    echo -e "${RED}Python 3 not found. Install Python first.${NC}"
    exit 1
fi

# ── Uninstall ──────────────────────────────────────────────────────────────

if [ "$ACTION" = "uninstall" ]; then
    echo -e "${CYAN}Uninstalling service...${NC}"

    if [ "$OS" = "linux" ]; then
        systemctl --user stop sentinel.service 2>/dev/null || true
        systemctl --user disable sentinel.service 2>/dev/null || true
        rm -f "${HOME}/.config/systemd/user/sentinel.service"
        systemctl --user daemon-reload
        echo -e "${GREEN}systemd service removed.${NC}"

    elif [ "$OS" = "macos" ]; then
        launchctl unload "${HOME}/Library/LaunchAgents/com.sentinel.agent.plist" 2>/dev/null || true
        rm -f "${HOME}/Library/LaunchAgents/com.sentinel.agent.plist"
        echo -e "${GREEN}launchd agent removed.${NC}"
    fi

    echo -e "${GREEN}Sentinel service uninstalled.${NC}"
    exit 0
fi

# ── Install Linux (systemd) ────────────────────────────────────────────────

if [ "$OS" = "linux" ]; then
    echo -e "${CYAN}Installing systemd user service...${NC}"

    mkdir -p "${HOME}/.config/systemd/user"

    cat > "${HOME}/.config/systemd/user/sentinel.service" << EOF
[Unit]
Description=Sentinel Voice Agent
After=network.target sound.target pulseaudio.service pipewire.service

[Service]
Type=simple
ExecStart=${PYTHON} ${SCRIPT_DIR}/sentinel_service.py
WorkingDirectory=${SCRIPT_DIR}
Restart=on-failure
RestartSec=5
Environment=DISPLAY=:0
Environment=XDG_RUNTIME_DIR=/run/user/$(id -u)
Environment=DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus

[Install]
WantedBy=default.target
EOF

    systemctl --user daemon-reload
    systemctl --user enable sentinel.service
    systemctl --user start sentinel.service

    echo -e "${GREEN}Sentinel installed as systemd user service.${NC}"
    echo ""
    echo "Commands:"
    echo "  systemctl --user status sentinel   # Check status"
    echo "  systemctl --user stop sentinel     # Stop"
    echo "  systemctl --user start sentinel    # Start"
    echo "  journalctl --user -u sentinel -f   # View logs"

# ── Install macOS (launchd) ────────────────────────────────────────────────

elif [ "$OS" = "macos" ]; then
    echo -e "${CYAN}Installing launchd agent...${NC}"

    mkdir -p "${HOME}/Library/LaunchAgents"

    cat > "${HOME}/Library/LaunchAgents/com.sentinel.agent.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.sentinel.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>${SCRIPT_DIR}/sentinel_service.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>${SCRIPT_DIR}</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>${SCRIPT_DIR}/sentinel_service.log</string>
    <key>StandardErrorPath</key>
    <string>${SCRIPT_DIR}/sentinel_service.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
EOF

    launchctl unload "${HOME}/Library/LaunchAgents/com.sentinel.agent.plist" 2>/dev/null || true
    launchctl load "${HOME}/Library/LaunchAgents/com.sentinel.agent.plist"

    echo -e "${GREEN}Sentinel installed as launchd agent.${NC}"
    echo ""
    echo "Commands:"
    echo "  launchctl list | grep sentinel     # Check status"
    echo "  launchctl unload ~/Library/LaunchAgents/com.sentinel.agent.plist  # Stop"
    echo "  launchctl load ~/Library/LaunchAgents/com.sentinel.agent.plist    # Start"
    echo "  tail -f sentinel_service.log      # View logs"
fi

echo ""
echo -e "${GREEN}Done. Sentinel will start automatically on next login.${NC}"
echo "To uninstall: bash install_service.sh uninstall"
