#!/bin/bash
# Setup script for Safe Auto-Updater

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Setting up Safe Auto-Updater..."

# Check prerequisites
echo "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found${NC}"

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Error: pip3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ pip3 found${NC}"

# Check Docker (optional)
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Docker found${NC}"
else
    echo -e "${YELLOW}⚠ Docker not found (optional)${NC}"
fi

# Check kubectl (optional)
if command -v kubectl &> /dev/null; then
    echo -e "${GREEN}✓ kubectl found${NC}"
else
    echo -e "${YELLOW}⚠ kubectl not found (optional)${NC}"
fi

# Check Helm (optional)
if command -v helm &> /dev/null; then
    echo -e "${GREEN}✓ Helm found${NC}"
else
    echo -e "${YELLOW}⚠ Helm not found (optional)${NC}"
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}Setup completed successfully!${NC}"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the application, use:"
echo "  python src/main.py -c configs/config.yaml"
