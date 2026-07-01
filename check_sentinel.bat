@echo off
REM Check if Sentinel is running
tasklist /FI "IMAGENAME eq pythonw.exe" 2>NUL | find /I "pythonw.exe" >NUL
if %ERRORLEVEL% EQU 0 (
    echo Sentinel IS running.
    tasklist /FI "IMAGENAME eq pythonw.exe" /FO TABLE
) else (
    echo Sentinel is NOT running.
    echo Start it: start_sentinel.bat
)
pause
