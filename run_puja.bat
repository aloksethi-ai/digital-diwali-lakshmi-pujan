@echo off
REM One-click launcher for the Digital Lakshmi Pujan app (Windows)
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    where py >nul 2>nul && (py -3 -m venv .venv) || (python -m venv .venv)
)
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt
python -m streamlit run app.py
pause
