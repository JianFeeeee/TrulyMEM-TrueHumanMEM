@echo off
echo ===== Building TrulyMEM for Windows =====

REM 切换到脚本所在目录的上一级目录（项目根目录）
cd /d "%~dp0.."
echo Project root: %CD%

python --version >nul 2>&1
if errorlevel 1 (
    echo Error: python not found
    exit /b 1
)

echo Installing dependencies...
pip install -r requirements.txt

echo Running PyInstaller...
python -m PyInstaller trulymem_entry.py ^
    --clean ^
    --onefile ^
    --console ^
    --name TrulyMEM ^
    --icon "pic/TrulyMEM.ico" ^
    --add-data "ui/styles;ui/styles" ^
    --add-data "core/prompts/templates;core/prompts/templates" ^
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
    --hidden-import ui ^
    --hidden-import ui.app ^
    --hidden-import ui.models ^
    --hidden-import ui.models.message ^
    --hidden-import ui.models.config ^
    --hidden-import ui.models.log_entry ^
    --hidden-import ui.widgets ^
    --hidden-import ui.handlers ^
    --hidden-import ui.services ^
    --hidden-import ui.services.config_manager ^
    --hidden-import ui.services.config_service ^
    --collect-all textual ^
    --noconfirm

echo ===== Build Complete =====
echo Binary: dist\TrulyMEM.exe
dir dist\TrulyMEM.exe
pause