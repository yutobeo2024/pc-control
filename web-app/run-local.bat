@echo off
echo ========================================
echo  Parental Control - Web App Local Server
echo ========================================
echo.
echo Starting server on http://localhost:8000
echo.
echo Open browser and go to:
echo   http://localhost:8000
echo.
echo To access from mobile (same WiFi):
echo   http://%COMPUTERNAME%:8000
echo.
echo Press Ctrl+C to stop server
echo.
cd public
python -m http.server 8000
