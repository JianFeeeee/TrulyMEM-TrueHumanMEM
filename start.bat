@echo off
title TrulyMEM

echo.
echo ========================================
echo   TrulyMEM Starting...
echo ========================================
echo.

python trulymem_entry.py

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start
    echo.
    echo Please check:
    echo 1. Python installed (python --version)
    echo 2. Dependencies installed (pip install -r requirements.txt)
    echo.
    pause
    exit /b 1
)

echo.
echo Application exited
pause
