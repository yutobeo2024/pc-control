@echo off
REM Cài đặt dependencies cho Windows Client

cd /d "%~dp0"
echo ========================================
echo  Parental Control - Install Dependencies
echo ========================================
echo.
echo Checking Python...
python --version
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.8 or later from https://www.python.org/
    pause
    exit /b 1
)
echo.
echo Installing dependencies...
echo.
pip install -r requirements.txt
echo.
echo ========================================
echo  Installation complete!
echo ========================================
echo.
echo To run the app:
echo   - Double-click run.bat (hidden mode)
echo   - Double-click run-debug.bat (debug mode)
echo.
pause
