# F3 - release verify: F2 fast gates + real OpenCode (agentic + social matrix).
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

& "$Root\scripts\stop_dev.ps1" -Port 8080
& "$Root\scripts\stop_dev.ps1" -Port 8090
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
    Write-Host "==> ingest"
    py -3 -m cli ingest
}

Write-Host "==> F2 quality gates (fast - no OpenCode matrix)"
py -3 scripts/run_quality_gates.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "==> F3 agentic (integration + agentic suites)"
py -3 -m pytest tests/integration tests/agentic -m agentic -q --tb=short
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "==> F3 social matrix (real OpenCode)"
py -3 -m pytest tests/social -m social -q --tb=short
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "RELEASE VERIFY: PASSED"
