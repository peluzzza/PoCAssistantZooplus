# Start zooplus Assistant API + Chat UI (http://127.0.0.1:8080/ui/)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "==> PoC root: $Root"

if (-not (Test-Path ".env")) {
    Write-Host "==> No .env found - run setup wizard first:"
    Write-Host "    .\scripts\setup_wizard.ps1"
    Write-Host "==> Falling back: copying .env.example -> .env"
    Copy-Item ".env.example" ".env"
}

# Load `.env` into this process (overrides stale shell vars from pytest/CI)
Get-Content ".env" -Encoding UTF8 | ForEach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith("#") -and $line -match "^([^=]+)=(.*)$") {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim().Trim('"').Trim("'")
        Set-Item -Path "Env:$name" -Value $value
    }
}

if (-not (Test-Path ".opencode\data\auth.json")) {
    Write-Host "==> Syncing OpenCode auth..."
    & "$Root\scripts\setup_opencode_local.ps1"
}

$manifest = "artifacts\index\manifest.json"
if (-not (Test-Path $manifest)) {
    Write-Host "==> Ingesting catalog..."
    py -3 -m cli ingest
}

$intent = if ($env:ZOOPLUS_INTENT_MODE) { $env:ZOOPLUS_INTENT_MODE } else { "(from .env, use agentic for real UI)" }
$synth = if ($env:ZOOPLUS_SYNTHESIS_MODE) { $env:ZOOPLUS_SYNTHESIS_MODE } else { "(from .env)" }
Write-Host ""
$port = if ($env:ZOOPLUS_DEV_PORT) { $env:ZOOPLUS_DEV_PORT } else { "8090" }
Write-Host "==> Starting API at http://127.0.0.1:${port}/ui/  (set ZOOPLUS_DEV_PORT=8080 if :8080 is free)"
Write-Host "    ZOOPLUS_INTENT_MODE=$intent  ZOOPLUS_SYNTHESIS_MODE=$synth"
Write-Host "    For sociable agent: INTENT_MODE=agentic + OpenCode auth (see .env.example)"
Write-Host "    Press Ctrl+C to stop"
Write-Host ""
& "$Root\scripts\stop_dev.ps1" -Port $port
py -3 -m uvicorn src.api.app:app --host 127.0.0.1 --port $port
