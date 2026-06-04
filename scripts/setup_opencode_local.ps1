# Copy existing OpenCode login into gitignored .opencode/data (no secrets in git).
# Or run interactive login: see docs/CHAT_UI.md

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$DataDir = Join-Path $Root ".opencode\data"
$GlobalAuth = Join-Path $env:USERPROFILE ".local\share\opencode\auth.json"
$LocalAuth = Join-Path $DataDir "auth.json"

New-Item -ItemType Directory -Force -Path $DataDir | Out-Null

if (Test-Path $GlobalAuth) {
    Copy-Item $GlobalAuth $LocalAuth -Force
    Write-Host "OK: copied global auth to $LocalAuth (gitignored)"
    exit 0
}

Write-Host "No global auth at $GlobalAuth"
Write-Host "Run: `$env:OPENCODE_DATA_DIR='$DataDir'; opencode auth login"
exit 1
