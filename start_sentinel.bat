@echo off
REM Start Sentinel in background mode (no console)
cd /d "%~dp0"
start "" pythonw sentinelw.pyw
echo Sentinel started in background. Check system tray indicator.
echo Press Ctrl+Alt+Q to quit, or run stop_sentinel.bat
