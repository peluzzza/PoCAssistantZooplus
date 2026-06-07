# Minimal functional smoke — fast, no OpenCode required (~2 min)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$env:ZOOPLUS_INTENT_MODE = "oracle"
$env:ZOOPLUS_SYNTHESIS_MODE = "template"
$env:ZOOPLUS_SOCIAL_SYNTHESIS = "agentic"
$env:ZOOPLUS_AGENT_CASCADE = "0"

Write-Host "==> Minimal smoke (unit + integration + 1 social matrix case; catalog via stream tests)"
py -3 -m pytest `
  tests/unit/test_synthesis.py `
  tests/unit/test_conversation.py `
  tests/unit/test_response_variety.py `
  tests/unit/test_intent_hints.py `
  tests/unit/test_agent_cascade.py `
  tests/unit/test_customer_status.py `
  tests/integration/test_chat_stream.py `
  tests/integration/test_agentic_fallback_routing.py `
  "tests/social/test_use_cases_matrix.py::test_use_case_matrix[UC-017]" `
  -q --tb=short
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "OK - minimal functional. Start UI: .\scripts\run_dev.ps1  (http://127.0.0.1:8090/ui/)"
