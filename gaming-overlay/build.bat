@echo off
title Build Gaming Co-Pilot — PyInstaller
echo.
echo  ==========================================
echo   Building standalone GamingOverlay.exe
echo  ==========================================
echo.

:: Install/upgrade PyInstaller first
pip install --quiet --upgrade pyinstaller

:: Build — onefile, no console window, bundle config.json next to the exe
pyinstaller ^
    --onefile ^
    --noconsole ^
    --name GamingOverlay ^
    --add-data "config.json;." ^
    --hidden-import=PySide6.QtCore ^
    --hidden-import=PySide6.QtWidgets ^
    --hidden-import=PySide6.QtGui ^
    --hidden-import=pyttsx3.drivers ^
    --hidden-import=pyttsx3.drivers.sapi5 ^
    --hidden-import=anthropic ^
    --hidden-import=mss ^
    --hidden-import=PIL._imaging ^
    --hidden-import=numpy ^
    --hidden-import=pynput.keyboard._win32 ^
    --hidden-import=pynput.mouse._win32 ^
    main.py

echo.
if exist "dist\GamingOverlay.exe" (
    echo  SUCCESS!  Your standalone .exe is at:
    echo    dist\GamingOverlay.exe
    echo.
    echo  Copy GamingOverlay.exe and config.json to the same folder anywhere you like.
) else (
    echo  BUILD FAILED — see the output above for errors.
)

pause
