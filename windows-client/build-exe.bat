@echo off
REM ============================================================
REM  Đóng gói Parental Control Client thành 1 file .exe độc lập
REM ============================================================
REM
REM  Trước khi build, đảm bảo đã:
REM    1. copy config.example.py config.py   (và điền FIREBASE_CONFIG)
REM    2. python set_password.py             (đổi mật khẩu khẩn cấp)
REM
REM  Vì config.py được NHÚNG vào .exe, hãy cấu hình xong rồi mới build.
REM  Kết quả: dist\ParentalControl.exe

chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   Build Parental Control .exe
echo ========================================
echo.

if not exist config.py (
    echo ERROR: Chua co config.py
    echo   Chay:  copy config.example.py config.py
    echo   Roi dien FIREBASE_CONFIG va chay python set_password.py
    pause
    exit /b 1
)

echo Kiem tra PyInstaller...
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo Cai PyInstaller...
    pip install pyinstaller
)

echo.
echo Dang build... (vai phut)
echo.
python -m PyInstaller ParentalControl.spec --noconfirm --clean

if errorlevel 1 (
    echo.
    echo ERROR: Build that bai
    pause
    exit /b 1
)

echo.
echo ========================================
echo   XONG!
echo ========================================
echo.
echo File: %CD%\dist\ParentalControl.exe
echo.
echo Buoc tiep theo:
echo   - Copy dist\ParentalControl.exe sang may con
echo   - Chay 1 lan de tao device_id.txt
echo   - Bat auto-start bang setup_autostart_exe.bat
echo.
pause
