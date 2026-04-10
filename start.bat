@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================
echo   Graph Memory TUI - Quick Start
echo ========================================
echo.
echo [INFO] Using embedded database (no Docker needed)
echo.

REM Step 1: Check Python
echo [Step 1/3] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    echo [INFO] Install from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python found

REM Step 2: Setup Virtual Environment
echo.
echo [Step 2/3] Setting up environment...
if not exist "venv" (
    echo [INFO] Creating venv...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create venv
        pause
        exit /b 1
    )
    echo [OK] Venv created
) else (
    echo [OK] Venv exists
)

call venv\Scripts\activate.bat

pip show textual >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install deps
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
) else (
    echo [OK] Dependencies ready
)

REM Step 3: Start Application
echo.
echo [Step 3/3] Starting application...
echo.
echo ========================================
echo   All systems ready!
echo ========================================
echo.
echo Database: Embedded SQLite (graph_memory.db)
echo No Docker required!
echo.
echo Starting TUI...
echo.

python -m graph_memory_tui.main

call venv\Scripts\deactivate.bat

echo.
echo Application closed.
pause
