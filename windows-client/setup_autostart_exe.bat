@echo off
REM ============================================================
REM  Bật auto-start cho bản ĐÓNG GÓI (ParentalControl.exe)
REM ============================================================
REM  Chạy trên MÁY CON. Chuột phải -> Run as administrator.
REM
REM  Khác với setup_autostart.bat (bản Python): script này trỏ thẳng tới
REM  ParentalControl.exe, KHÔNG cần Python cài trên máy.
REM
REM  Đặt file này CẠNH ParentalControl.exe rồi chạy.

cd /d "%~dp0"

set TASK_NAME=ParentalControlClient
set EXE_PATH=%~dp0ParentalControl.exe

if not exist "%EXE_PATH%" (
    echo ERROR: Khong tim thay ParentalControl.exe canh file nay
    echo   Dat setup_autostart_exe.bat cung thu muc voi ParentalControl.exe
    pause
    exit /b 1
)

echo ========================================
echo   Setup Auto-Start (ban .exe)
echo ========================================
echo.
echo EXE: %EXE_PATH%
echo.

set XML_FILE=%TEMP%\parental_control_exe_task.xml

(
echo ^<?xml version="1.0" encoding="UTF-16"?^>
echo ^<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task"^>
echo   ^<RegistrationInfo^>
echo     ^<Description^>Parental Control Client (packaged) - Auto start with Windows^</Description^>
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
echo       ^<Command^>"%EXE_PATH%"^</Command^>
echo       ^<WorkingDirectory^>%~dp0^</WorkingDirectory^>
echo     ^</Exec^>
echo   ^</Actions^>
echo ^</Task^>
) > "%XML_FILE%"

schtasks /create /tn "%TASK_NAME%" /xml "%XML_FILE%" /f

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   SUCCESS! Auto-start da bat
    echo ========================================
    echo.
    echo App se tu chay khi dang nhap Windows.
    echo Go bo: remove_autostart.bat  ^(dung chung cho ca 2 ban^)
    echo.
) else (
    echo.
    echo ERROR: Tao task that bai - hay Run as administrator
    echo.
)

del "%XML_FILE%" >nul 2>&1
pause
