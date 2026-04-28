#!/bin/bash
set -e

echo "===== Building TrulyMEM AppImage ====="

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"
echo "Project root: $PROJECT_ROOT"

# ── 检查依赖 ──────────────────────────────────────────────────────────────
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found"; exit 1
fi

APPIMAGE_TOOL="${APPIMAGE_TOOL:-appimagetool}"
if ! command -v "$APPIMAGE_TOOL" &> /dev/null && [ ! -f "$APPIMAGE_TOOL" ]; then
    echo "Warning: $APPIMAGE_TOOL not found, will try to create AppDir only"
    SKIP_APPIMAGE=1
fi

# ── 虚拟环境 ──────────────────────────────────────────────────────────────
VENV_DIR="$PROJECT_ROOT/.venv_build"
echo "Creating virtual environment: $VENV_DIR"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt

echo "Cleaning previous builds..."
rm -rf build/dist build/__pycache__ 2>/dev/null || true

# ── 打包 ──────────────────────────────────────────────────────────────────
echo "================================"
echo "Building TrulyMEM (TUI + Web embedded)"
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
    --hidden-import core \
    --hidden-import core.embedded_db \
    --hidden-import core.graph_client \
    --hidden-import core.tool_executor \
    --hidden-import core.tool_limiter \
    --hidden-import core.tools \
    --hidden-import core.tools.memory_tools \
    --hidden-import core.prompts \
    --hidden-import core.prompts.prompt_manager \
    --hidden-import core.server \
    --hidden-import core.client \
    --hidden-import core.migrate \
    --hidden-import core.activity_recorder \
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
    --hidden-import werkzeug \
    --collect-all textual \
    --noconfirm

# ── 创建 AppDir ───────────────────────────────────────────────────────────
APP_NAME="TrulyMEM"
APP_DIR="$PROJECT_ROOT/build/${APP_NAME}.AppDir"
mkdir -p "$APP_DIR/usr/bin"
cp "dist/TrulyMEM" "$APP_DIR/usr/bin/TrulyMEM"

# Desktop 文件
cat > "$APP_DIR/${APP_NAME}.desktop" << EOF
[Desktop Entry]
Name=TrulyMEM
Comment=TrueHumanMEM - AI Memory System
Exec=TrulyMEM
Icon=${APP_NAME}
Terminal=true
Type=Application
Categories=Utility;AI;
EOF

# 图标
mkdir -p "$APP_DIR/usr/share/icons/hicolor/256x256/apps"
# 如果有图标文件就复制，否则创建占位
if [ -f "pic/image.png" ]; then
    cp "pic/image.png" "$APP_DIR/usr/share/icons/hicolor/256x256/apps/${APP_NAME}.png"
    cp "pic/image.png" "$APP_DIR/${APP_NAME}.png"
else
    # 创建最小占位图标（1x1 透明 PNG）
    echo -n "" > "$APP_DIR/${APP_NAME}.png"
fi

# AppRun
cat > "$APP_DIR/AppRun" << 'APPRUN'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/usr/bin:${PATH}"
exec "${HERE}/usr/bin/TrulyMEM" "$@"
APPRUN
chmod +x "$APP_DIR/AppRun"

# ── 构建 AppImage ────────────────────────────────────────────────────────
if [ "$SKIP_APPIMAGE" != "1" ]; then
    echo "================================"
    echo "Building AppImage"
    echo "================================"
    # 支持 ARCH 环境变量
    ARCH="${ARCH:-$(uname -m)}" "$APPIMAGE_TOOL" "$APP_DIR" "dist/TrulyMEM-${ARCH}.AppImage"
    echo "AppImage: dist/TrulyMEM-${ARCH}.AppImage"
else
    echo "(Skipped AppImage packaging, AppDir ready at $APP_DIR)"
fi

echo "================================"
echo "===== Build Complete ====="
echo "Binary: dist/TrulyMEM"
ls -la dist/

deactivate
rm -rf "$VENV_DIR"
echo "Build finished successfully!"
