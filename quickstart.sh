#!/bin/bash
# Quick start script for UV setup

set -e

echo "=================================="
echo "Method Analysis Dashboard Setup"
echo "=================================="
echo ""

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "❌ UV is not installed!"
    echo ""
    echo "Install UV with:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    exit 1
fi

echo "✅ UV is installed"
echo ""

# Create virtual environment and install dependencies
echo "📦 Installing dependencies with UV..."
uv sync
echo ""

# Run setup script
echo "🔧 Running setup script..."
uv run python setup.py
echo ""

echo "=================================="
echo "✅ Setup complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Move your CSV to data/ folder"
echo "2. Add your config JSON files to config/"
echo "3. Edit config.py to set CSV_PATH"
echo "4. Run dashboard:"
echo "   uv run python dashboard.py"
echo ""
