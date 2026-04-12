#!/bin/bash
set -e

echo "===== Building TrulyMEM for Linux ====="

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "Project root: $PROJECT_ROOT"

echo "Installing dependencies..."
pip3 install -r requirements.txt 2>/dev/null || pip install -r requirements.txt

echo "Cleaning previous builds..."
rm -rf build/dist build/__pycache__ 2>/dev/null || true

echo "Running PyInstaller..."
python3 -m PyInstaller trulymem_entry.py \
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
    --collect-all textual \
    --noconfirm

echo "===== Build Complete ====="
echo "Binary: dist/TrulyMEM"
ls -la dist/