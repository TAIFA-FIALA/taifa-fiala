#!/bin/bash
# TAIFA-FIALA Dependency Migration Script
# Migrates from mixed dependency management to unified requirements.txt

echo "=== TAIFA-FIALA Dependency Migration ==="

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install all dependencies from unified requirements.txt
echo "Installing unified dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Dependency migration complete!"
echo ""
echo "Usage:"
echo "  Development: source venv/bin/activate"
echo "  Production: Use the unified requirements.txt in Docker"
echo ""
echo "Simplified Structure:"
echo "  ✅ Root: requirements.txt (unified)"
echo "  ❌ Backend: requirements.txt (removed)"
echo "  ❌ Data processors: pyproject.toml (removed)"
echo "  ✅ Frontend: package.json (unchanged)"
