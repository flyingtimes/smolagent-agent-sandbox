@echo off
for /f "tokens=1,* delims==" %%a in (.env) do (
    set "%%a=%%~b"
)
cd docker-sandbox
python sandbox_main.py