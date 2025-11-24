@echo off
echo ========================================
echo Teams Typing Bot - Daily Setup
echo ========================================
echo.
echo This will:
echo 1. Open Edge browser for you to log into Teams
echo 2. Save your session
echo 3. Run the bot in headless mode
echo.
pause

REM Check if Edge is already running
tasklist /FI "IMAGENAME eq msedge.exe" 2>NUL | find /I /N "msedge.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Warning: Edge is already running. Close all Edge windows first.
    echo Press any key to continue anyway, or Ctrl+C to cancel...
    pause >nul
)

echo.
echo ========================================
echo Step 1: Starting Edge for login
echo ========================================
echo.

REM Start Edge with remote debugging
start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222 --user-data-dir="C:\temp\edge_debug" "https://teams.microsoft.com/v2/"

echo Waiting for Edge to start (10 seconds)...
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo IMPORTANT: Complete these steps:
echo ========================================
echo.
echo 1. In the Edge browser that opened:
echo    - Log into Teams (complete 2FA if needed)
echo    - Wait for Teams to fully load
echo    - Navigate to your self-chat
echo.
echo 2. Once you're in your self-chat, come back here
echo    and press any key to save your session...
echo.
pause

echo.
echo ========================================
echo Step 2: Saving your session
echo ========================================
echo.

python save_session.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error: Failed to save session!
    echo Make sure Edge is still open with Teams loaded.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Step 3: Closing visible browser
echo ========================================
echo.
echo You can now close the Edge window.
echo Press any key when ready to start headless bot...
pause

echo.
echo ========================================
echo Step 4: Starting headless bot
echo ========================================
echo.
echo The bot will now run in the background (headless).
echo It will edit a single message with the current time every 3 minutes.
echo.
echo Press Ctrl+C to stop the bot at any time.
echo.

python teams_heartbeat.py

echo.
echo ========================================
echo Bot stopped
echo ========================================
echo.
pause
