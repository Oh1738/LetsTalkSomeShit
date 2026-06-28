@echo off
title Gaming Co-Pilot Overlay
echo.
echo  ========================================
echo   Gaming Co-Pilot Overlay — starting...
echo  ========================================
echo.

:: Check that Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  ERROR: Python not found.
    echo  Install Python 3.11+ from https://python.org and add it to PATH.
    pause
    exit /b 1
)

:: Check that the API key is set
if "%ANTHROPIC_API_KEY%"=="" (
    echo  WARNING: ANTHROPIC_API_KEY is not set in this session.
    echo  The overlay will show an error bubble when it starts.
    echo  Fix: run  setx ANTHROPIC_API_KEY "sk-ant-..."  then reopen this window.
    echo.
)

python "%~dp0main.py"
pause
