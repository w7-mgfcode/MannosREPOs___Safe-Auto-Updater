#!/bin/bash
# Rollback script for Safe Auto-Updater

set -e

# Configuration
RESOURCE_TYPE="${1:-deployment}"
RESOURCE_NAME="${2}"
NAMESPACE="${3:-default}"
REVISION="${4}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

if [ -z "$RESOURCE_NAME" ]; then
    echo -e "${RED}Error: Resource name is required${NC}"
    echo "Usage: $0 <resource-type> <resource-name> [namespace] [revision]"
    echo "Example: $0 deployment myapp default 2"
    exit 1
fi

echo "Rolling back ${RESOURCE_TYPE}/${RESOURCE_NAME} in namespace ${NAMESPACE}..."

case "$RESOURCE_TYPE" in
    "deployment"|"statefulset"|"daemonset")
        if [ -n "$REVISION" ]; then
            echo "Rolling back to revision ${REVISION}..."
            kubectl rollout undo "${RESOURCE_TYPE}/${RESOURCE_NAME}" \
                --namespace="${NAMESPACE}" \
                --to-revision="${REVISION}"
        else
            echo "Rolling back to previous revision..."
            kubectl rollout undo "${RESOURCE_TYPE}/${RESOURCE_NAME}" \
                --namespace="${NAMESPACE}"
        fi
        
        echo "Waiting for rollback to complete..."
        kubectl rollout status "${RESOURCE_TYPE}/${RESOURCE_NAME}" \
            --namespace="${NAMESPACE}" \
            --timeout=5m
        
        echo -e "${GREEN}Rollback completed successfully${NC}"
        ;;
    
    "helm")
        if [ -n "$REVISION" ]; then
            echo "Rolling back Helm release ${RESOURCE_NAME} to revision ${REVISION}..."
            helm rollback "${RESOURCE_NAME}" "${REVISION}" --namespace="${NAMESPACE}"
        else
            echo "Rolling back Helm release ${RESOURCE_NAME} to previous revision..."
            helm rollback "${RESOURCE_NAME}" --namespace="${NAMESPACE}"
        fi
        
        echo -e "${GREEN}Helm rollback completed successfully${NC}"
        ;;
    
    *)
        echo -e "${RED}Error: Unsupported resource type: ${RESOURCE_TYPE}${NC}"
        echo "Supported types: deployment, statefulset, daemonset, helm"
        exit 1
        ;;
esac
