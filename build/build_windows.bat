@echo off
setlocal enabledelayedexpansion

echo ===== Building TrulyMEM for Windows =====

set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
cd /d "%PROJECT_ROOT%"
echo Project root: %CD%

where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: python not found
    exit /b 1
)

set VENV_DIR=%PROJECT_ROOT%\.venv_build
echo Creating virtual environment: %VENV_DIR%
python -m venv "%VENV_DIR%"
call "%VENV_DIR%\Scripts\activate.bat"
pip install --upgrade pip
pip install -r requirements.txt

echo Cleaning previous builds...
if exist build\dist rmdir /s /q build\dist
if exist build\__pycache__ rmdir /s /q build\__pycache__

echo ================================
echo Building TrulyMEM ^(TUI + Web embedded^)
echo ================================
python -m PyInstaller trulymem_entry.py ^
    --clean --onefile --console --name TrulyMEM ^
    --add-data "ui/styles;ui/styles" ^
    --add-data "core/prompts/templates;core/prompts/templates" ^
    --add-data "static;static" ^
    --add-data "templates;templates" ^
    --add-data "web_api.py;." ^
    --hidden-import textual ^
    --hidden-import textual.app ^
    --hidden-import textual.widgets ^
    --hidden-import textual.css ^
    --hidden-import openai ^
    --hidden-import openai._client ^
    --hidden-import neo4j ^
    --hidden-import sqlite3 ^
    --hidden-import core ^
    --hidden-import core.embedded_db ^
    --hidden-import core.graph_client ^
    --hidden-import core.tool_executor ^
    --hidden-import core.tool_limiter ^
    --hidden-import core.tools ^
    --hidden-import core.tools.memory_tools ^
    --hidden-import core.prompts ^
    --hidden-import core.prompts.prompt_manager ^
    --hidden-import core.server ^
    --hidden-import core.client ^
    --hidden-import core.migrate ^
    --hidden-import core.activity_recorder ^
    --hidden-import ui ^
    --hidden-import ui.app ^
    --hidden-import ui.login_screen ^
    --hidden-import ui.models ^
    --hidden-import ui.models.message ^
    --hidden-import ui.models.config ^
    --hidden-import ui.models.log_entry ^
    --hidden-import ui.widgets ^
    --hidden-import ui.handlers ^
    --hidden-import ui.services ^
    --hidden-import ui.services.config_manager ^
    --hidden-import ui.services.config_service ^
    --hidden-import web_api ^
    --hidden-import flask ^
    --hidden-import flask_cors ^
    --hidden-import werkzeug ^
    --collect-all textual ^
    --noconfirm

echo ================================
echo ===== Build Complete =====
echo Binary: dist\TrulyMEM.exe
dir dist\

call deactivate
if exist "%VENV_DIR%" rmdir /s /q "%VENV_DIR%"
echo Build finished successfully!
endlocal
