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
rm -rf dist/ build/trulymem/ 2>/dev/null || true

echo "================================"
echo "Building TrulyMEM (TUI + Web embedded)"
echo "================================"
python -m PyInstaller --clean build/trulymem.spec --noconfirm

echo "================================"
echo "===== Build Complete ====="
echo "Binary: dist/TrulyMEM"
ls -la dist/

deactivate
rm -rf "$VENV_DIR"
echo "Build finished successfully!"