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

# ── 尝试 venv 隔离构建，失败则用系统环境 ──
USE_VENV=false
if python3 -m venv --help &>/dev/null; then
    VENV_DIR="$PROJECT_ROOT/.venv_build"
    if python3 -m venv "$VENV_DIR" 2>/dev/null; then
        source "$VENV_DIR/bin/activate"
        USE_VENV=true
        echo "Using virtual environment"
        pip install --upgrade pip -q
        pip install -r requirements.txt -q
    else
        echo "Warning: venv creation failed, falling back to system Python"
    fi
else
    echo "Warning: python3-venv not available, falling back to system Python"
fi

if [ "$USE_VENV" = false ]; then
    pip install -r requirements.txt --break-system-packages -q 2>/dev/null || \
        pip install -r requirements.txt -q 2>/dev/null || true
fi

echo "Cleaning previous builds..."
rm -rf dist/ build/trulymem/ 2>/dev/null || true

echo "================================"
echo "Building TrulyMEM (TUI + Web embedded)"
echo "================================"
python3 -m PyInstaller --clean build/trulymem.spec --noconfirm

echo "================================"
echo "===== Build Complete ====="
echo "Binary: dist/TrulyMEM"
ls -la dist/

if [ "$USE_VENV" = true ]; then
    deactivate 2>/dev/null || true
    rm -rf "$VENV_DIR"
fi
echo "Build finished successfully!"