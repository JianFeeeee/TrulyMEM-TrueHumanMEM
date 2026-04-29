#!/bin/bash
set -e

echo "===== Building TrulyMEM AppImage ====="

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"
echo "Project root: $PROJECT_ROOT"

APP_NAME="TrulyMEM"
APP_DIR="$PROJECT_ROOT/build/appimage-build"

echo "Cleaning..."
rm -rf "$APP_DIR" dist/ build/trulymem/ 2>/dev/null || true

# Step 1: Build with PyInstaller (uses icon from .spec)
echo "Step 1: PyInstaller build..."
python3 -m PyInstaller --clean build/trulymem.spec --noconfirm

# Step 2: Prepare AppDir structure
echo "Step 2: Preparing AppDir..."
mkdir -p "$APP_DIR/usr/bin"
mkdir -p "$APP_DIR/usr/share/applications"
mkdir -p "$APP_DIR/usr/share/icons/hicolor/256x256/apps"

cp "dist/$APP_NAME" "$APP_DIR/usr/bin/"
if [ -f "pic/image.png" ]; then
    cp "pic/image.png" "$APP_DIR/usr/share/icons/hicolor/256x256/apps/${APP_NAME}.png"
    cp "pic/image.png" "$APP_DIR/${APP_NAME}.png"
else
    echo -n "" > "$APP_DIR/${APP_NAME}.png"
fi

cat > "$APP_DIR/${APP_NAME}.desktop" <<EOF
[Desktop Entry]
Name=${APP_NAME}
Exec=${APP_NAME}
Icon=${APP_NAME}
Type=Application
Categories=Utility;
Terminal=true
EOF

cp "$APP_DIR/${APP_NAME}.desktop" "$APP_DIR/usr/share/applications/"

cat > "$APP_DIR/AppRun" <<'APPRUN'
#!/bin/bash
HERE="$(dirname "$(readlink -f "$0")")"
exec "$HERE/usr/bin/TrulyMEM" "$@"
APPRUN
chmod +x "$APP_DIR/AppRun"

# Step 3: Build AppImage (requires appimagetool)
echo "Step 3: Building AppImage..."
if command -v appimagetool &> /dev/null; then
    appimagetool "$APP_DIR" "dist/${APP_NAME}.AppImage"
    echo "AppImage: dist/${APP_NAME}.AppImage"
    ls -la "dist/${APP_NAME}.AppImage"
else
    echo "appimagetool not found. AppDir ready at: $APP_DIR"
    echo "Install appimagetool and run: appimagetool '$APP_DIR' 'dist/${APP_NAME}.AppImage'"
fi

echo "===== AppImage Build Complete ====="