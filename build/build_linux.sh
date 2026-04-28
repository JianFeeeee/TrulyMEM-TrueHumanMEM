#!/bin/bash
set -e

echo "===== Building TrulyMEM for Linux ====="

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"
echo "Project root: $PROJECT_ROOT"

if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found"; exit 1
fi

VENV_DIR="$PROJECT_ROOT/.venv_build"
echo "Creating virtual environment: $VENV_DIR"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt

echo "Cleaning previous builds..."
rm -rf build/dist build/__pycache__ 2>/dev/null || true

# 共用 hidden imports（TUI + Web 都需要的核心库）
CORE_HIDDEN=(
    --hidden-import core
    --hidden-import core.embedded_db
    --hidden-import core.graph_client
    --hidden-import core.tool_executor
    --hidden-import core.tool_limiter
    --hidden-import core.tools
    --hidden-import core.tools.memory_tools
    --hidden-import core.prompts
    --hidden-import core.prompts.prompt_manager
    --hidden-import core.server
    --hidden-import core.client
    --hidden-import core.migrate
    --hidden-import core.activity_recorder
)

echo "================================"
echo "1️⃣  Build TUI: TrulyMEM"
echo "================================"
python -m PyInstaller trulymem_entry.py \
    --clean --onefile --console --name TrulyMEM \
    --add-data "ui/styles:ui/styles" \
    --add-data "core/prompts/templates:core/prompts/templates" \
    --add-data "static:static" \
    --add-data "templates:templates" \
    --add-data "web_api.py:." \
    --hidden-import textual \
    --hidden-import textual.app \
    --hidden-import textual.widgets \
    --hidden-import textual.css \
    --hidden-import openai \
    --hidden-import openai._client \
    --hidden-import neo4j \
    --hidden-import sqlite3 \
    "${CORE_HIDDEN[@]}" \
    --hidden-import ui \
    --hidden-import ui.app \
    --hidden-import ui.login_screen \
    --hidden-import ui.models \
    --hidden-import ui.models.message \
    --hidden-import ui.models.config \
    --hidden-import ui.models.log_entry \
    --hidden-import ui.widgets \
    --hidden-import ui.handlers \
    --hidden-import ui.services \
    --hidden-import ui.services.config_manager \
    --hidden-import ui.services.config_service \
    --hidden-import web_api \
    --hidden-import flask \
    --hidden-import flask_cors \
    --collect-all textual \
    --noconfirm

echo "================================"
echo "2️⃣  Build Web: trulymem-web"
echo "================================"
python -m PyInstaller web_api.py \
    --clean --onefile --console --name trulymem-web \
    --add-data "templates:templates" \
    --add-data "static:static" \
    --hidden-import flask \
    --hidden-import flask_cors \
    "${CORE_HIDDEN[@]}" \
    --noconfirm

echo "================================"
echo "===== Build Complete ====="
echo "Binary: dist/TrulyMEM"
echo "Binary: dist/trulymem-web"
ls -la dist/

deactivate
rm -rf "$VENV_DIR"
echo "Build finished successfully!"
