#!/bin/bash
# Health check script for Safe Auto-Updater

set -e

# Configuration
CONTAINER_NAME="${CONTAINER_NAME:-safe-auto-updater}"
TIMEOUT="${TIMEOUT:-30}"
INTERVAL="${INTERVAL:-5}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Starting health check for ${CONTAINER_NAME}..."

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${RED}Error: Container ${CONTAINER_NAME} is not running${NC}"
    exit 1
fi

# Check container status
STATUS=$(docker inspect --format='{{.State.Status}}' "${CONTAINER_NAME}")
if [ "$STATUS" != "running" ]; then
    echo -e "${RED}Error: Container status is ${STATUS}${NC}"
    exit 1
fi

echo -e "${GREEN}Container is running${NC}"

# Check container health if health check is defined
if docker inspect --format='{{.State.Health.Status}}' "${CONTAINER_NAME}" 2>/dev/null | grep -q "healthy"; then
    echo -e "${GREEN}Container health check passed${NC}"
    exit 0
elif docker inspect --format='{{.State.Health.Status}}' "${CONTAINER_NAME}" 2>/dev/null | grep -q "unhealthy"; then
    echo -e "${RED}Container health check failed${NC}"
    exit 1
else
    echo -e "${YELLOW}No health check defined, assuming healthy${NC}"
    exit 0
fi
