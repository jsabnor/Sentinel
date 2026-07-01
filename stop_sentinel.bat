@echo off
REM Stop all Sentinel background processes
taskkill /FI "IMAGENAME eq pythonw.exe" /FI "WINDOWTITLE eq sentinelw*" /F >nul 2>&1
taskkill /FI "IMAGENAME eq pythonw.exe" /F >nul 2>&1
echo Sentinel stopped.
