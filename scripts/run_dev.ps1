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

$intent = if ($env:ZOOPLUS_INTENT_MODE) { $env:ZOOPLUS_INTENT_MODE } else { "(from .env — use agentic for real UI)" }
$synth = if ($env:ZOOPLUS_SYNTHESIS_MODE) { $env:ZOOPLUS_SYNTHESIS_MODE } else { "(from .env)" }
Write-Host ""
Write-Host "==> Starting API at http://127.0.0.1:8080/ui/"
Write-Host "    ZOOPLUS_INTENT_MODE=$intent  ZOOPLUS_SYNTHESIS_MODE=$synth"
Write-Host "    For sociable agent: INTENT_MODE=agentic + OpenCode auth (see .env.example)"
Write-Host "    Press Ctrl+C to stop"
Write-Host ""
py -3 -m uvicorn src.api.app:app --host 127.0.0.1 --port 8080 --reload
