@echo off
for /f "tokens=1,* delims==" %%a in (.env) do (
    set "%%a=%%~b"
)
if "%1"=="" (
    python agent_code.py
) else (
    python %1
)