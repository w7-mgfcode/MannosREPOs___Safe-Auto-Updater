#!/bin/bash
#
# Bash/cURL examples for Safe Auto-Updater API
#

set -e

BASE_URL="${API_URL:-http://localhost:8000}"

echo "=== Safe Auto-Updater API Examples (cURL) ==="
echo "Base URL: $BASE_URL"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ===== 1. Health Check =====
echo -e "${GREEN}1. Health Check${NC}"
curl -s "$BASE_URL/api/v1/health" | jq '.status, .version, .uptime_seconds'
echo ""

# ===== 2. Version Info =====
echo -e "${GREEN}2. Version Information${NC}"
curl -s "$BASE_URL/api/v1/version" | jq '.'
echo ""

# ===== 3. Configuration =====
echo -e "${GREEN}3. Current Configuration${NC}"
curl -s "$BASE_URL/api/v1/config" | jq '.auto_update_enabled, .semver_gates'
echo ""

# ===== 4. Asset Statistics =====
echo -e "${GREEN}4. Asset Statistics${NC}"
curl -s "$BASE_URL/api/v1/assets/stats" | jq '.'
echo ""

# ===== 5. List Assets =====
echo -e "${GREEN}5. List Assets (first 5)${NC}"
curl -s "$BASE_URL/api/v1/assets/?page_size=5" | jq '.total, .assets[] | {name, type: .asset_type, version: .current_version}'
echo ""

# ===== 6. List Assets with Filter =====
echo -e "${GREEN}6. List Assets (filtered by namespace=production)${NC}"
curl -s "$BASE_URL/api/v1/assets/?namespace=production" | jq '.total'
echo ""

# ===== 7. Evaluate Patch Update =====
echo -e "${GREEN}7. Evaluate Patch Update (1.0.0 -> 1.0.1)${NC}"
curl -s -X POST "$BASE_URL/api/v1/updates/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "current_version": "1.0.0",
    "new_version": "1.0.1"
  }' | jq '{change_type, decision, safe, reason}'
echo ""

# ===== 8. Evaluate Minor Update =====
echo -e "${GREEN}8. Evaluate Minor Update (1.0.0 -> 1.1.0)${NC}"
curl -s -X POST "$BASE_URL/api/v1/updates/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "current_version": "1.0.0",
    "new_version": "1.1.0"
  }' | jq '{change_type, decision, safe, reason}'
echo ""

# ===== 9. Evaluate Major Update =====
echo -e "${GREEN}9. Evaluate Major Update (1.0.0 -> 2.0.0)${NC}"
curl -s -X POST "$BASE_URL/api/v1/updates/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "current_version": "1.0.0",
    "new_version": "2.0.0"
  }' | jq '{change_type, decision, safe, reason}'
echo ""

# ===== 10. Scan Assets (Dry Run) =====
echo -e "${GREEN}10. Scan Assets${NC}"
curl -s -X POST "$BASE_URL/api/v1/updates/scan" \
  -H "Content-Type: application/json" \
  -d '{
    "docker": false,
    "kubernetes": false,
    "force_refresh": false
  }' | jq '{status, assets_discovered, duration_seconds}'
echo ""

# ===== 11. Update History =====
echo -e "${GREEN}11. Update History${NC}"
curl -s "$BASE_URL/api/v1/updates/history?limit=5" | jq 'length'
echo ""

# ===== 12. Prometheus Metrics =====
echo -e "${GREEN}12. Prometheus Metrics (sample)${NC}"
curl -s "$BASE_URL/api/v1/metrics" | grep -E "^safe_updater_" | head -5
echo ""

# ===== 13. Get Specific Asset =====
echo -e "${GREEN}13. Get Specific Asset (if exists)${NC}"
ASSET_ID=$(curl -s "$BASE_URL/api/v1/assets/?page_size=1" | jq -r '.assets[0].id // "none"')
if [ "$ASSET_ID" != "none" ]; then
  curl -s "$BASE_URL/api/v1/assets/$ASSET_ID" | jq '{id, name, current_version, status}'
else
  echo "No assets found"
fi
echo ""

# ===== 14. Response Time Check =====
echo -e "${GREEN}14. Response Time Check${NC}"
RESPONSE=$(curl -s -w "\nX-Response-Time: %{time_total}s\n" "$BASE_URL/api/v1/health" -o /dev/null)
echo "$RESPONSE"
echo ""

echo "=== Examples Complete ==="
