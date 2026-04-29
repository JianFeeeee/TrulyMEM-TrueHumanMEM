@echo off
setlocal enabledelayedexpansion

echo ===== Building TrulyMEM for Windows =====

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
cd /d "%PROJECT_ROOT%"
echo Project root: %PROJECT_ROOT%

echo Creating virtual environment: .venv_build
python -m venv .venv_build
call .venv_build\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt

echo Cleaning previous builds...
if exist dist rmdir /s /q dist
if exist build\trulymem rmdir /s /q build\trulymem

echo ================================
echo Building TrulyMEM (TUI + Web embedded)
echo ================================
python -m PyInstaller --clean build\trulymem.spec --noconfirm

echo ================================
echo ===== Build Complete =====
echo Binary: dist\TrulyMEM.exe
dir dist

call .venv_build\Scripts\deactivate.bat
if exist .venv_build rmdir /s /q .venv_build

echo Build finished successfully!
endlocal