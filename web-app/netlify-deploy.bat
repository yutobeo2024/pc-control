@echo off
echo ========================================
echo  Deploy to Netlify
echo ========================================
echo.

REM Check if netlify CLI is installed
where netlify >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Netlify CLI not found!
    echo.
    echo Installing Netlify CLI...
    npm install -g netlify-cli
    echo.
)

echo Logging in to Netlify...
netlify login

echo.
echo Deploying to production...
netlify deploy --prod --dir=public

echo.
echo ========================================
echo  Deploy complete!
echo ========================================
echo.
echo Your site is now live!
echo Check the URL above and update it in:
echo   windows-client\main.py
echo.
pause
