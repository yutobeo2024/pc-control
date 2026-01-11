@echo off
echo ========================================
echo   Remove Auto-Start from Windows
echo ========================================
echo.

set TASK_NAME=ParentalControlClient

echo Removing scheduled task...
schtasks /delete /tn "%TASK_NAME%" /f

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   SUCCESS! Auto-start removed
    echo ========================================
    echo.
    echo The Parental Control Client will no longer start automatically.
    echo.
) else (
    echo.
    echo ========================================
    echo   Task not found or error occurred
    echo ========================================
    echo.
)

pause
