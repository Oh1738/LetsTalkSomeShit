@echo off
title Gaming Co-Pilot Overlay

:: Use the venv Python directly — no activation needed
set PYTHON="%~dp0.venv\Scripts\python.exe"

if not exist %PYTHON% (
    echo ERROR: Virtual environment not found.
    echo Please run these commands once in PowerShell:
    echo   cd "%~dp0"
    echo   python -m venv .venv
    echo   .\.venv\Scripts\Activate.ps1
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

if "%ANTHROPIC_API_KEY%"=="" (
    echo WARNING: ANTHROPIC_API_KEY is not set.
    echo Run this in PowerShell: setx ANTHROPIC_API_KEY "sk-ant-..."
    echo Then reopen this window.
    echo.
)

%PYTHON% "%~dp0main.py"
pause
