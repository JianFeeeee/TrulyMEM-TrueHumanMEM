@echo off
echo Building Windows binary...

python --version >nul 2>&1
if errorlevel 1 (
    echo Error: python not found
    exit /b 1
)

pip install -r requirements.txt

python -m PyInstaller --clean --onefile --console ^
    --add-data "ui/styles;ui/styles" ^
    --add-data "core/prompts/templates;core/prompts/templates" ^
    --hidden-import textual ^
    --hidden-import openai ^
    --hidden-import neo4j ^
    --collect-all textual ^
    trulymem_entry.py

echo Done! Binary: dist\TrulyMEM.exe
pause