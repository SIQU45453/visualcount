@echo off
cd /d "%~dp0"
if not exist .venv (
  echo First start: setting up, this takes a few minutes...
  python -m venv .venv || (echo Python not found. Install it from python.org and tick "Add python.exe to PATH". & pause & exit /b)
  .venv\Scripts\python -m pip install --upgrade pip
  .venv\Scripts\pip install torch --index-url https://download.pytorch.org/whl/cpu
  .venv\Scripts\pip install -r requirements.txt
)
.venv\Scripts\python server.py
pause
