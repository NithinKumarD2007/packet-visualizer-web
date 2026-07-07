@echo off
cd /d "%~dp0"
python -m uvicorn backend.app.main:app --reload
pause