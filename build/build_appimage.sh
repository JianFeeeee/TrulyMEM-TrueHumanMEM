#!/bin/bash
set -e
echo "===== Building TrulyMEM AppImage for Linux ====="
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found"
    exit 1
fi
APPDIR="$PROJECT_ROOT/TrulyMEM.AppDir"
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/trulymem"
mkdir -p "$APPDIR/usr/share/trulymem-web"

echo "===== Step 1: Build binaries with PyInstaller ====="
VENV_DIR="$PROJECT_ROOT/.venv_appimage"
rm -rf "$VENV_DIR"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller
rm -rf "$PROJECT_ROOT/build/pyinstaller_build" "$PROJECT_ROOT/dist"

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

echo "Running PyInstaller for TUI..."
pyinstaller trulymem_entry.py \
    --clean --onefile --console --name TrulyMEM \
    --distpath "$PROJECT_ROOT/dist" \
    --workpath "$PROJECT_ROOT/build/pyinstaller_build/tui" \
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

echo "Running PyInstaller for Web..."
pyinstaller web_api.py \
    --clean --onefile --console --name trulymem-web \
    --distpath "$PROJECT_ROOT/dist" \
    --workpath "$PROJECT_ROOT/build/pyinstaller_build/web" \
    --add-data "templates:templates" \
    --add-data "static:static" \
    --hidden-import flask \
    --hidden-import flask_cors \
    "${CORE_HIDDEN[@]}" \
    --noconfirm

cp "$PROJECT_ROOT/dist/TrulyMEM" "$APPDIR/usr/bin/"
cp "$PROJECT_ROOT/dist/trulymem-web" "$APPDIR/usr/bin/"
cp "$PROJECT_ROOT/trulymem_entry.py" "$APPDIR/usr/share/trulymem/"

echo "===== Step 2: Create AppImage structure ====="
cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash
set -e
SELF=$(readlink -f "$0")
APPDIR=$(dirname "$SELF")
export PATH="$APPDIR/usr/bin:$PATH"
exec "$APPDIR/usr/bin/TrulyMEM" "$@"
EOF
chmod +x "$APPDIR/AppRun"

cat > "$APPDIR/trulymem.desktop" << 'EOF'
[Desktop Entry]
Name=TrulyMEM
Comment=AI Memory System with Long-term Memory
Exec=TrulyMEM %U
Icon=trulymem
Terminal=true
Type=Application
Categories=Utility;X-AI;
EOF

# Copy icon
if [ -f "$PROJECT_ROOT/pic/TrulyMEM.png" ]; then
    cp "$PROJECT_ROOT/pic/TrulyMEM.png" "$APPDIR/trulymem.png"
elif [ -f "$PROJECT_ROOT/pic/TrulyMEM.iconset/icon_256x256.png" ]; then
    cp "$PROJECT_ROOT/pic/TrulyMEM.iconset/icon_256x256.png" "$APPDIR/trulymem.png"
elif [ -f "$PROJECT_ROOT/pic/TrulyMEM.iconset/icon_128x128.png" ]; then
    cp "$PROJECT_ROOT/pic/TrulyMEM.iconset/icon_128x128.png" "$APPDIR/trulymem.png"
else
    echo "Warning: No icon file found"
fi

APPIMAGE="$PROJECT_ROOT/TrulyMEM.AppImage"
rm -f "$APPIMAGE"

echo "===== Step 3: Package as AppImage ====="
cd /tmp
if ! command -v appimagetool &> /dev/null; then
    echo "Downloading appimagetool..."
    wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage -O appimagetool 2>/dev/null || \
    curl -sL https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage -o appimagetool
    chmod +x appimagetool 2>/dev/null || true
fi
cd "$PROJECT_ROOT"
if [ -x /tmp/appimagetool ]; then
    /tmp/appimagetool "$APPDIR" "$APPIMAGE" || echo "appimagetool failed, keeping AppDir"
elif command -v appimagetool &> /dev/null; then
    appimagetool "$APPDIR" "$APPIMAGE"
else
    echo "Warning: appimagetool not available, AppDir at: $APPDIR"
fi

echo "===== Build Complete ====="
[ -f "$APPIMAGE" ] && echo "AppImage: $APPIMAGE" && ls -la "$APPIMAGE"
[ -d "$APPDIR" ] && echo "AppDir: $APPDIR"

echo "===== Cleanup ====="
deactivate
rm -rf "$VENV_DIR"
rm -rf "$PROJECT_ROOT/build/pyinstaller_build"
rm -f /tmp/appimagetool
if [ -f "$APPIMAGE" ]; then
    rm -rf "$APPDIR"
fi
echo "Done!"
