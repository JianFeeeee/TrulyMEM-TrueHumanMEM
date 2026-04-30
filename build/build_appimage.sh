#!/bin/bash
set -euo pipefail

echo "===== Building TrulyMEM AppImage ====="

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"
echo "Project root: $PROJECT_ROOT"

APP_NAME="TrulyMEM"
APP_DIR="$PROJECT_ROOT/build/appimage-build"

# ── Step 1: 复用 build_linux.sh 完成 PyInstaller 构建 ──
echo ""
echo "Step 1: Running build_linux.sh (PyInstaller build)..."
bash "$SCRIPT_DIR/build_linux.sh"

# ── Step 2: 检查 dist/ 中是否有二进制 ──
echo ""
echo "Step 2: Checking PyInstaller output..."
if [ ! -f "dist/$APP_NAME" ]; then
    echo "Error: dist/$APP_NAME not found after build_linux.sh"; exit 1
fi
echo "✅ Found dist/$APP_NAME ($(ls -lh "dist/$APP_NAME" | awk '{print $5}'))"

# ── Step 3: 组织 AppDir 结构 ──
echo ""
echo "Step 3: Preparing AppDir structure..."
rm -rf "$APP_DIR" 2>/dev/null || true
mkdir -p "$APP_DIR/usr/bin"
mkdir -p "$APP_DIR/usr/share/applications"
mkdir -p "$APP_DIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$APP_DIR/usr/share/icons/hicolor/48x48/apps"

cp "dist/$APP_NAME" "$APP_DIR/usr/bin/"

# 图标处理
ICON_SOURCE=""
if [ -f "pic/image.png" ]; then
    ICON_SOURCE="pic/image.png"
elif [ -f "pic/TrulyMEM.ico" ]; then
    echo "⚠️  No pic/image.png found; .ico will not display as AppImage icon"
    echo "   To generate a PNG: convert pic/TrulyMEM.ico pic/image.png"
fi

if [ -n "$ICON_SOURCE" ]; then
    cp "$ICON_SOURCE" "$APP_DIR/usr/share/icons/hicolor/256x256/apps/${APP_NAME}.png"
    cp "$ICON_SOURCE" "$APP_DIR/usr/share/icons/hicolor/48x48/apps/${APP_NAME}.png"
    cp "$ICON_SOURCE" "$APP_DIR/${APP_NAME}.png"
    echo "✅ Icon: $ICON_SOURCE"
else
    echo "⚠️  No icon found, creating placeholder"
    touch "$APP_DIR/${APP_NAME}.png"
fi

# .desktop 文件
cat > "$APP_DIR/${APP_NAME}.desktop" <<EOF
[Desktop Entry]
Name=${APP_NAME}
Comment=True Human Memory - TUI & Web Mode
Exec=${APP_NAME}
Icon=${APP_NAME}
Type=Application
Categories=Utility;Office;
Terminal=true
StartupNotify=true
EOF

cp "$APP_DIR/${APP_NAME}.desktop" "$APP_DIR/usr/share/applications/"

# AppRun 入口
cat > "$APP_DIR/AppRun" <<'APPRUN'
#!/bin/bash
HERE="$(dirname "$(readlink -f "$0")")"
exec "$HERE/usr/bin/TrulyMEM" "$@"
APPRUN
chmod +x "$APP_DIR/AppRun"

# ── Step 4: 打包 AppImage ──
echo ""
echo "Step 4: Building AppImage..."
if command -v appimagetool &> /dev/null; then
    ARCH="${ARCH:-$(uname -m)}" appimagetool "$APP_DIR" "dist/${APP_NAME}.AppImage"
    echo "✅ AppImage: dist/${APP_NAME}.AppImage"
    ls -lh "dist/${APP_NAME}.AppImage"
else
    echo "⚠️  appimagetool not found. AppDir ready at: $APP_DIR"
    echo ""
    echo "To complete manually, install appimagetool:"
    echo "  wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-$(uname -m).AppImage"
    echo "  chmod +x appimagetool-*.AppImage"
    echo "  ./appimagetool-*.AppImage '$APP_DIR' 'dist/${APP_NAME}.AppImage'"
    echo ""
    echo "AppDir contents:"
    find "$APP_DIR" -type f | head -20
fi

echo ""
echo "===== AppImage Build Complete ====="
