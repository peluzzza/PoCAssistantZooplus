# F3-fast - release smoke (~3 min). Full OpenCode matrix: run_release_verify.ps1 (CI/nightly only).
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "==> F3-fast: smoke_minimal (stream progress + oracle/template)"
.\scripts\smoke_minimal.ps1
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "RELEASE FAST: PASSED (skip full social matrix locally; use CI for OpenCode)"
