#!/bin/bash
# Test script for Safe Auto-Updater

set -e

# Change to script directory
cd "$(dirname "$0")/.."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run install.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run tests
echo "Running tests..."
pytest tests/ -v --cov=safe_auto_updater --cov-report=term-missing

echo ""
echo "Tests complete!"
