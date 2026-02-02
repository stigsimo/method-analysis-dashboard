#!/usr/bin/env bash
set -o errexit

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🔧 Running setup to download data..."
python setup.py

echo "✅ Build complete!"