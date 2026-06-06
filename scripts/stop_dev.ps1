param([int]$Port = 8080)
# Stop all processes bound to the dev port (stale uvicorn stacks on Windows).
$ErrorActionPreference = "SilentlyContinue"
$pids = @(
    Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty OwningProcess -Unique
)
foreach ($procId in $pids) {
    if ($procId -and $procId -ne 0) {
        Write-Host "Stopping PID $procId on :$Port"
        Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
    }
}
Start-Sleep -Seconds 2
$left = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($left) {
    Write-Host "WARN: port $Port still in use - try: `$env:ZOOPLUS_DEV_PORT=8090; .\scripts\run_dev.ps1"
} else {
    Write-Host "Port $Port cleared."
}
