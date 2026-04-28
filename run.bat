@echo off
echo ============================================
echo   Magic Formula Dashboard - India
echo   Data Source: Screener.in (LIVE)
echo ============================================
echo.
echo [1/3] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please install Python 3.9+ from https://python.org/downloads
    pause
    exit /b 1
)

echo [2/3] Installing dependencies (first run only)...
python -m pip install -q -r requirements.txt

echo [3/3] Launching dashboard at http://localhost:8501 ...
echo.
echo *** Press Ctrl+C in this window to stop ***
echo.
python -m streamlit run magic_formula_app.py
pause
