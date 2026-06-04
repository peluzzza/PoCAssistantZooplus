# Start zooplus Assistant API + Chat UI (http://127.0.0.1:8080/ui/)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "==> PoC root: $Root"

if (-not (Test-Path ".env")) {
    Write-Host "==> Copying .env.example -> .env (edit ZOOPLUS_* as needed)"
    Copy-Item ".env.example" ".env"
}

if (-not (Test-Path ".opencode\data\auth.json")) {
    Write-Host "==> OpenCode auth (optional): .\scripts\setup_opencode_local.ps1"
}

$manifest = "artifacts\index\manifest.json"
if (-not (Test-Path $manifest)) {
    Write-Host "==> Ingesting catalog..."
    py -3 -m cli ingest
}

Write-Host ""
Write-Host "==> Starting API at http://127.0.0.1:8080/ui/"
Write-Host "    Press Ctrl+C to stop"
Write-Host ""
py -3 -m uvicorn src.api.app:app --host 127.0.0.1 --port 8080 --reload
