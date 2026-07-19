#!/bin/bash
set -euo pipefail

BUILD_DIR=".build/lambda"
ZIP_FILE=".build/webhook.zip"

echo "=== Building Lambda ZIP ==="

# Clean previous build
rm -rf .build
mkdir -p "$BUILD_DIR"

# Check if uv is available
if command -v uv &> /dev/null; then
    echo "Using uv for dependency installation..."
    uv pip install --python .venv/bin/python -t "$BUILD_DIR" .
else
    echo "Using pip for dependency installation..."
    .venv/bin/pip install --quiet --upgrade pip setuptools
    .venv/bin/pip install --quiet -t "$BUILD_DIR" .
fi

# Copy app code
echo "Copying application code..."
cp -r app "$BUILD_DIR/"
cp -r alembic "$BUILD_DIR/"
cp alembic.ini "$BUILD_DIR/"

# Create ZIP
echo "Creating ZIP archive..."
cd "$BUILD_DIR"
zip -qr "../../$ZIP_FILE" .
cd ../..

# Show result
ZIP_SIZE=$(du -h "$ZIP_FILE" | cut -f1)
echo "=== Build complete ==="
echo "Output: $ZIP_FILE ($ZIP_SIZE)"
