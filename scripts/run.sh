#!/bin/bash
# Run script for Safe Auto-Updater

set -e

# Change to script directory
cd "$(dirname "$0")/.."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running install script..."
    ./scripts/install.sh
fi

# Activate virtual environment
source venv/bin/activate

# Run the application
echo "Starting Safe Auto-Updater..."
python -m safe_auto_updater.cli "$@"
