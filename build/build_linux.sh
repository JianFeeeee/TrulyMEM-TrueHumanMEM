#!/bin/bash
set -e

echo "===== Building TrulyMEM for Linux ====="

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "Project root: $PROJECT_ROOT"

if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found"
    exit 1
fi

# 创建并激活虚拟环境
VENV_DIR="$PROJECT_ROOT/.venv_build"

echo "Creating virtual environment: $VENV_DIR"
python3 -m venv "$VENV_DIR"

echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "Upgrading pip in virtual environment..."
pip install --upgrade pip

echo "Installing dependencies in virtual environment..."
pip install -r requirements.txt

echo "Cleaning previous builds..."
rm -rf build/dist build/__pycache__ 2>/dev/null || true

echo "Running PyInstaller..."
python -m PyInstaller trulymem_entry.py \
    --clean \
    --onefile \
    --console \
    --name TrulyMEM \
    --add-data "ui/styles:ui/styles" \
    --add-data "core/prompts/templates:core/prompts/templates" \
    --hidden-import textual \
    --hidden-import textual.app \
    --hidden-import textual.widgets \
    --hidden-import textual.css \
    --hidden-import openai \
    --hidden-import openai._client \
    --hidden-import neo4j \
    --hidden-import sqlite3 \
    --hidden-import core \
    --hidden-import core.embedded_db \
    --hidden-import core.graph_client \
    --hidden-import core.tool_executor \
    --hidden-import core.tool_limiter \
    --hidden-import core.tools \
    --hidden-import core.tools.memory_tools \
    --hidden-import core.prompts \
    --hidden-import core.prompts.prompt_manager \
    --hidden-import ui \
    --hidden-import ui.app \
    --hidden-import ui.models \
    --hidden-import ui.models.message \
    --hidden-import ui.models.config \
    --hidden-import ui.models.log_entry \
    --hidden-import ui.widgets \
    --hidden-import ui.handlers \
    --hidden-import ui.services \
    --hidden-import ui.services.config_manager \
    --hidden-import ui.services.config_service \
    --collect-all textual \
    --noconfirm

echo "===== Build Complete ====="
echo "Binary: dist/TrulyMEM"
ls -la dist/

# 清理虚拟环境
echo "Cleaning up virtual environment..."
deactivate
rm -rf "$VENV_DIR"

echo "Build finished successfully!"