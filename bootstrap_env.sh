#!/bin/bash

# ============================================================================
# Bootstrap Script for AI Edge Deployment Environment (Raspberry Pi Compatible)
# ============================================================================
# This script creates a clean Python virtual environment and installs all
# required dependencies with versions known to be compatible with TensorFlow Lite Runtime.
# It is intended to ensure reproducibility and prevent compatibility issues
# during development or deployment on ARM and x86_64 systems.
# ============================================================================

echo "Initializing Python virtual environment for the edge AI solution..."

# Ensure Python 3.10 is available
if ! command -v python3.10 &> /dev/null; then
    echo "Python 3.10 is not installed or not available in PATH."
    echo "Please install Python 3.10 to proceed."
    exit 1
fi

# Clean up any existing environment
if [ -d ".venv" ]; then
    echo "Removing existing virtual environment (.venv)..."
    rm -rf .venv
fi

# Create a new virtual environment
python3.10 -m venv .venv
source .venv/bin/activate

echo "Installing compatible Python packages..."

# Upgrade pip and install stable, compatible versions
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Environment setup complete."
echo "To activate the environment, run:"
echo "    source .venv/bin/activate"
echo ""
echo "To test model compatibility, run:"
echo "    python src/validate_model.py"
echo ""

exit 0