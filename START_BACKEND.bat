@echo off
title BlockStat Pro - Backend Server
color 0A

echo.
echo ============================================================
echo   BlockStat Pro - Backend Server
echo ============================================================
echo.
echo Starting backend server on port 5000...
echo.
echo IMPORTANT: Keep this window open while using the frontend!
echo.
echo ============================================================
echo.

cd /d "%~dp0backend"

echo [1/3] Checking dependencies...
call npm install >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [2/3] Dependencies OK
echo [3/3] Starting server...
echo.
echo ============================================================
echo.

call npm run dev

pause

