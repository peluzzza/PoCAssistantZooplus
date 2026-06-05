@echo off
REM Double-click or: scripts\setup_wizard.cmd
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_wizard.ps1"
pause
