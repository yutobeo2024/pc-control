@echo off
REM ============================================================
REM  Bat auto-start cho ban dong goi (ParentalControl.exe)
REM ============================================================
REM  Chay tren MAY CON. Chuot phai -> Run as administrator.
REM  Dat file nay CANH ParentalControl.exe roi chay.
REM
REM  Phai dang nhap bang chinh tai khoan Windows ma tre dung: task gan
REM  trigger "khi dang nhap" vao tai khoan tao ra no. Cuoi script co in ra
REM  tai khoan that su duoc gan de kiem chung.
REM ============================================================

setlocal
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
echo   Setup Auto-Start ^(ban .exe^)
echo ========================================
echo.
echo EXE       : %EXE_PATH%
echo Dang chay : %USERDOMAIN%\%USERNAME%
echo.

REM ---------------------------------------------------------------- Tao task
REM Truoc day script ghi ra mot file XML roi nap bang `schtasks /create /xml`.
REM File do khai encoding="UTF-16" nhung dau `>` cua cmd ghi ra ANSI, nen tuy
REM may ma schtasks tu choi voi "The task XML is malformed" - that bai am tham,
REM nguoi cai tuong da xong. Goi schtasks truc tiep cho chac.
REM
REM Dau ngoac kep long \" la de duong dan co dau cach van chay dung.
schtasks /create /tn "%TASK_NAME%" /tr "\"%EXE_PATH%\"" /sc onlogon /rl highest /f
if errorlevel 1 (
    echo.
    echo ERROR: Tao task that bai.
    echo   - Da chuot phai -^> Run as administrator chua?
    pause
    exit /b 1
)

REM ------------------------------------------------------- Sua 3 mac dinh xau
REM schtasks de lai ba thiet lap mac dinh vo hieu hoa he thong trong im lang:
REM   ExecutionTimeLimit = 72 gio -> Task Scheduler TU DUNG app sau 3 ngay chay
REM       lien tuc. May chi ngu chu khong tat thi du 3 ngay la het bao ve.
REM   DisallowStartIfOnBatteries = True -> laptop chay pin thi app khong khoi dong
REM   StopIfGoingOnBatteries = True -> dang chay ma rut sac la app bi dung.
REM       Tre rut day dien la xong.
echo.
echo Dang sua thiet lap task...
powershell -NoProfile -Command "$s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -DontStopOnIdleEnd -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Seconds 0); Set-ScheduledTask -TaskName '%TASK_NAME%' -Settings $s | Out-Null"
if errorlevel 1 (
    echo.
    echo CANH BAO: Khong sua duoc thiet lap task.
    echo   Task van chay, nhung se tu dung sau 72 gio va bi chan khi may chay pin.
    echo   Sua tay trong Task Scheduler: bo tick "Stop the task if it runs longer
    echo   than" va hai o "battery power" trong tab Conditions.
)

REM ------------------------------------------------------------- Kiem chung
echo.
echo ========================================
echo   Ket qua
echo ========================================
powershell -NoProfile -Command "$t = Get-ScheduledTask -TaskName '%TASK_NAME%'; 'Tai khoan  : ' + $t.Principal.UserId; 'Quyen      : ' + $t.Principal.RunLevel; 'Gioi han TG: ' + $t.Settings.ExecutionTimeLimit + '   (can PT0S = khong gioi han)'; 'Chan pin   : ' + $t.Settings.DisallowStartIfOnBatteries + ' / ' + $t.Settings.StopIfGoingOnBatteries + '   (can False / False)'; 'Trigger    : ' + $t.Triggers[0].CimClass.CimClassName"

echo.
echo So "Tai khoan" o tren voi lenh:  whoami
echo Khac nhau -^> app se khoi dong khi NGUOI KHAC dang nhap, khong phai tre.
echo.
echo Nghiem thu that: khoi dong lai may, dang nhap, man khoa phai tu hien len.
echo Go bo: remove_autostart.bat
echo.
pause
