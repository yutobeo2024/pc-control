@echo off
echo ========================================
echo   Setup Auto-Start with Windows
echo ========================================
echo.

REM Get current directory
set SCRIPT_DIR=%~dp0
set PYTHON_SCRIPT=%SCRIPT_DIR%main.py

REM Find Python executable
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_EXE=python
) else (
    echo ERROR: Python not found in PATH!
    echo Please install Python or add it to PATH
    pause
    exit /b 1
)

echo Creating scheduled task...
echo.

REM Create XML for task scheduler
set TASK_NAME=ParentalControlClient
set XML_FILE=%TEMP%\parental_control_task.xml

(
echo ^<?xml version="1.0" encoding="UTF-16"?^>
echo ^<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task"^>
echo   ^<RegistrationInfo^>
echo     ^<Description^>Parental Control Client - Auto start with Windows^</Description^>
echo   ^</RegistrationInfo^>
echo   ^<Triggers^>
echo     ^<LogonTrigger^>
echo       ^<Enabled^>true^</Enabled^>
echo     ^</LogonTrigger^>
echo   ^</Triggers^>
echo   ^<Principals^>
echo     ^<Principal id="Author"^>
echo       ^<LogonType^>InteractiveToken^</LogonType^>
echo       ^<RunLevel^>HighestAvailable^</RunLevel^>
echo     ^</Principal^>
echo   ^</Principals^>
echo   ^<Settings^>
echo     ^<MultipleInstancesPolicy^>IgnoreNew^</MultipleInstancesPolicy^>
echo     ^<DisallowStartIfOnBatteries^>false^</DisallowStartIfOnBatteries^>
echo     ^<StopIfGoingOnBatteries^>false^</StopIfGoingOnBatteries^>
echo     ^<AllowHardTerminate^>false^</AllowHardTerminate^>
echo     ^<StartWhenAvailable^>true^</StartWhenAvailable^>
echo     ^<RunOnlyIfNetworkAvailable^>false^</RunOnlyIfNetworkAvailable^>
echo     ^<IdleSettings^>
echo       ^<StopOnIdleEnd^>false^</StopOnIdleEnd^>
echo       ^<RestartOnIdle^>false^</RestartOnIdle^>
echo     ^</IdleSettings^>
echo     ^<AllowStartOnDemand^>true^</AllowStartOnDemand^>
echo     ^<Enabled^>true^</Enabled^>
echo     ^<Hidden^>false^</Hidden^>
echo     ^<RunOnlyIfIdle^>false^</RunOnlyIfIdle^>
echo     ^<WakeToRun^>false^</WakeToRun^>
echo     ^<ExecutionTimeLimit^>PT0S^</ExecutionTimeLimit^>
echo     ^<Priority^>7^</Priority^>
echo   ^</Settings^>
echo   ^<Actions Context="Author"^>
echo     ^<Exec^>
echo       ^<Command^>pythonw.exe^</Command^>
echo       ^<Arguments^>"%PYTHON_SCRIPT%"^</Arguments^>
echo       ^<WorkingDirectory^>%SCRIPT_DIR%^</WorkingDirectory^>
echo     ^</Exec^>
echo   ^</Actions^>
echo ^</Task^>
) > "%XML_FILE%"

REM Import task
schtasks /create /tn "%TASK_NAME%" /xml "%XML_FILE%" /f

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   SUCCESS! Auto-start configured
    echo ========================================
    echo.
    echo Task Name: %TASK_NAME%
    echo.
    echo The Parental Control Client will now start automatically when Windows boots.
    echo.
    echo To REMOVE auto-start, run: remove_autostart.bat
    echo.
) else (
    echo.
    echo ========================================
    echo   ERROR: Failed to create task
    echo ========================================
    echo.
    echo Please run this script as Administrator!
    echo Right-click and select "Run as administrator"
    echo.
)

REM Cleanup
del "%XML_FILE%" >nul 2>&1

pause
