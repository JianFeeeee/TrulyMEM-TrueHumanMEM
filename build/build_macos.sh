#!/bin/bash
set -e

echo "Building macOS binary..."

if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found"
    exit 1
fi

pip3 install -r requirements.txt

python3 -m PyInstaller --clean --onefile --console \
    --add-data "ui/styles:ui/styles" \
    --add-data "core/prompts/templates:core/prompts/templates" \
    --hidden-import textual \
    --hidden-import openai \
    --hidden-import neo4j \
    --collect-all textual \
    trulymem_entry.py

echo "Done! Binary: dist/TrulyMEM"