#!/bin/bash
set -euo pipefail

echo "===== Building TrulyMEM for Linux ====="

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"
echo "Project root: $PROJECT_ROOT"

# ── 前置检查 ──
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found"; exit 1
fi

if [ ! -f requirements.txt ]; then
    echo "Error: requirements.txt not found in $PROJECT_ROOT"; exit 1
fi

# ── 检测 python3-venv ──
VENV_AVAILABLE=false
if python3 -c "import ensurepip" 2>/dev/null && python3 -m venv --help &>/dev/null; then
    VENV_AVAILABLE=true
else
    echo "⚠️  python3-venv 未安装（或缺少 ensurepip），建议安装以获得干净构建环境："
    echo "   sudo apt install python3-venv    # Debian/Ubuntu"
    echo "   sudo dnf install python3-virtualenv  # Fedora"
    echo "将使用系统 Python 环境继续（依赖全局包）..."
    echo ""
fi

# ── 尝试 venv 隔离构建，失败则用系统环境 ──
USE_VENV=false
if [ "$VENV_AVAILABLE" = true ]; then
    VENV_DIR="$PROJECT_ROOT/.venv_build"
    echo "Creating virtual environment..."
    if python3 -m venv "$VENV_DIR" 2>/dev/null; then
        source "$VENV_DIR/bin/activate"
        USE_VENV=true
        echo "✅ Using virtual environment: $VENV_DIR"
        pip install --upgrade pip -q
        pip install -r requirements.txt -q
    else
        echo "⚠️  venv creation failed, falling back to system Python"
    fi
fi

if [ "$USE_VENV" = false ]; then
    echo "Installing dependencies (system Python)..."
    pip install -r requirements.txt --break-system-packages -q 2>/dev/null || \
        pip install -r requirements.txt -q 2>/dev/null || {
            echo "⚠️  pip install failed, trying pip3..."
            pip3 install -r requirements.txt --break-system-packages -q 2>/dev/null || \
            pip3 install -r requirements.txt -q 2>/dev/null || \
            echo "⚠️  Some dependencies may be missing; build will proceed anyway"
        }
fi

# ── 清理旧构建 ──
echo ""
echo "Cleaning previous builds..."
rm -rf dist/ build/trulymem/ 2>/dev/null || true

# ── PyInstaller 构建 ──
echo ""
echo "================================"
echo "Building TrulyMEM (TUI + Web embedded)"
echo "================================"
python3 -m PyInstaller --clean build/trulymem.spec --noconfirm

# ── 创建 Linux `.desktop` 文件（打包图标不能嵌入 ELF，通过 .desktop 引用）──
echo ""
echo "Generating .desktop file for Linux..."
BINARY_PATH="$(cd dist && pwd)/TrulyMEM"
ICON_PATH="$(cd pic && pwd)/image.png"

cat > "dist/TrulyMEM.desktop" <<EOF
[Desktop Entry]
Name=TrulyMEM
Comment=True Human Memory - TUI & Web Mode
Exec=${BINARY_PATH}
Icon=${ICON_PATH}
Terminal=true
Type=Application
Categories=Utility;Office;
StartupNotify=true
EOF

chmod +x "dist/TrulyMEM.desktop"
echo "✅ dist/TrulyMEM.desktop created (icon: pic/image.png)"

# ── 构建完成 ──
echo ""
echo "================================"
echo "===== Build Complete ====="
echo "Binary:     dist/TrulyMEM"
echo "Desktop:    dist/TrulyMEM.desktop"
echo "------------------------------"
ls -lh dist/ 2>/dev/null || ls -la dist/
echo "================================"

# ── 清理 venv ──
if [ "$USE_VENV" = true ]; then
    deactivate 2>/dev/null || true
    rm -rf "$VENV_DIR"
    echo "Virtual environment cleaned up."
fi

echo "Build finished successfully!"
