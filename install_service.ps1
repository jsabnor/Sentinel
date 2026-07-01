# Sentinel - Windows Service Installer
# Installs Sentinel to start automatically at login.
# No admin rights required.
# Run: powershell -ExecutionPolicy Bypass -File install_service.ps1

$ErrorActionPreference = "Stop"
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Find startup folder
$startupDir = [Environment]::GetFolderPath("Startup")
$shortcutPath = Join-Path $startupDir "Sentinel.lnk"

$pythonw = (Get-Command pythonw -ErrorAction SilentlyContinue).Source
if (-not $pythonw) {
    $pythonDir = Split-Path -Parent (Get-Command python).Source
    $pythonw = Join-Path $pythonDir "pythonw.exe"
}

if (-not (Test-Path $pythonw)) {
    Write-Host "pythonw.exe not found at: $pythonw" -ForegroundColor Red
    Write-Host "Install Python first (python.org)" -ForegroundColor Red
    exit 1
}

Write-Host "=== Sentinel Windows Service Installer ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Project:    $projectDir"
Write-Host "Python:     $pythonw"
Write-Host "Startup:    $startupDir"
Write-Host ""

$action = Read-Host "Install (i) or Uninstall (u)? [i/u]"

if ($action -eq "u") {
    if (Test-Path $shortcutPath) {
        Remove-Item $shortcutPath -Force
        Write-Host "Removed: $shortcutPath" -ForegroundColor Green
    } else {
        Write-Host "No startup shortcut found." -ForegroundColor Yellow
    }

    # Also try to remove scheduled task if exists
    schtasks /Delete /TN "Sentinel Agent" /F 2>$null

    Write-Host "Sentinel uninstalled." -ForegroundColor Green
    exit 0
}

if (Test-Path $shortcutPath) {
    Remove-Item $shortcutPath -Force
}

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = $pythonw
$Shortcut.Arguments = """$projectDir\sentinelw.pyw"""
$Shortcut.WorkingDirectory = $projectDir
$Shortcut.WindowStyle = 7
$Shortcut.Description = "Sentinel Voice Agent"
$Shortcut.Save()

Write-Host "Startup shortcut created: $shortcutPath" -ForegroundColor Green
Write-Host ""
Write-Host "Sentinel will start automatically when you log in." -ForegroundColor Cyan
Write-Host ""
Write-Host "Start now:  pythonw sentinelw.pyw  (or start_sentinel.bat)"
Write-Host "Stop:       Ctrl+Alt+Q  or  stop_sentinel.bat"
Write-Host "Uninstall:  powershell -File install_service.ps1  (choose u)"
