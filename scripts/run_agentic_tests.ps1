# Real OpenCode integration tests (no mocks). Requires auth + opencode on PATH.
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

& "$Root\scripts\setup_opencode_local.ps1"
if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env" }

Get-Content ".env" -Encoding UTF8 | ForEach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith("#") -and $line -match "^([^=]+)=(.*)$") {
        Set-Item -Path "Env:$($matches[1].Trim())" -Value $matches[2].Trim().Trim('"').Trim("'")
    }
}

$manifest = "artifacts\index\manifest.json"
if (-not (Test-Path $manifest)) {
    Write-Host "==> Ingesting catalog..."
    py -3 -m cli ingest
}

Write-Host "==> Agentic integration tests (real LLM via OpenCode)"
py -3 -m pytest tests/integration -m agentic -v --tb=short
