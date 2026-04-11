@echo off
title TrulyMEM - Installation

echo.
echo ========================================
echo   TrulyMEM - Installation Script
echo ========================================
echo.

REM Check Python
echo [1/4] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python not found
    echo.
    echo Please install Python 3.8+
    echo Download: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
python --version
echo [OK] Python installed
echo.

REM Create virtual environment
echo [2/4] Creating virtual environment...
if exist "venv" (
    echo [SKIP] Virtual environment already exists
) else (
    python -m venv venv
    if errorlevel 1 (
        echo [X] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)
echo.

REM Activate and install dependencies
echo [3/4] Installing dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if errorlevel 1 (
    echo [X] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Create config file
echo [4/4] Creating config file...
if not exist "config.json" (
    echo {"api_key": "", "model": "deepseek-chat", "base_url": "https://api.deepseek.com"} > config.json
    echo [OK] Config file created
) else (
    echo [SKIP] Config file already exists
)
echo.

echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Now you can run start.bat to launch the app
echo.
pause
