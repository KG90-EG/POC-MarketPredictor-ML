#!/bin/bash
# Rate Limiting Test Script
# Tests the API rate limiter (60 requests/minute)

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
BACKEND_URL="${1:-http://localhost:8000}"
RATE_LIMIT=60
TEST_DURATION=60
REQUESTS_TO_SEND=70  # Exceed the limit

echo -e "${BLUE}🔒 Rate Limiting Test${NC}"
echo "=================================="
echo "Backend URL: $BACKEND_URL"
echo "Rate Limit: $RATE_LIMIT requests/minute"
echo "Test: Sending $REQUESTS_TO_SEND requests"
echo ""

# Test function
test_rate_limit() {
    echo -e "${YELLOW}Starting rate limit test...${NC}"
    
    SUCCESS_COUNT=0
    RATE_LIMITED_COUNT=0
    ERROR_COUNT=0
    
    START_TIME=$(date +%s)
    
    for i in $(seq 1 $REQUESTS_TO_SEND); do
        # Make request
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/health" 2>/dev/null)
        
        if [ "$HTTP_CODE" == "200" ]; then
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
            echo -ne "\rRequests: $i | Success: $SUCCESS_COUNT | Rate Limited: $RATE_LIMITED_COUNT"
        elif [ "$HTTP_CODE" == "429" ]; then
            RATE_LIMITED_COUNT=$((RATE_LIMITED_COUNT + 1))
            echo -ne "\rRequests: $i | Success: $SUCCESS_COUNT | Rate Limited: $RATE_LIMITED_COUNT"
        else
            ERROR_COUNT=$((ERROR_COUNT + 1))
        fi
        
        # Small delay to simulate realistic traffic
        sleep 0.5
    done
    
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    echo ""
    echo ""
    echo -e "${BLUE}=================================="
    echo "Test Results"
    echo "==================================${NC}"
    echo ""
    echo "Total Requests:    $REQUESTS_TO_SEND"
    echo "Successful (200):  $SUCCESS_COUNT"
    echo "Rate Limited (429): $RATE_LIMITED_COUNT"
    echo "Errors:            $ERROR_COUNT"
    echo "Duration:          ${DURATION}s"
    echo ""
    
    # Calculate rate
    REQUESTS_PER_MINUTE=$(echo "scale=2; ($SUCCESS_COUNT / $DURATION) * 60" | bc)
    echo "Actual Rate:       ${REQUESTS_PER_MINUTE} req/min"
    echo "Expected Limit:    $RATE_LIMIT req/min"
    echo ""
    
    # Verify rate limiting is working
    if [ $RATE_LIMITED_COUNT -gt 0 ]; then
        echo -e "${GREEN}✓ Rate limiting is WORKING${NC}"
        echo "  - $RATE_LIMITED_COUNT requests were rate limited (429)"
        echo "  - Rate limiter is protecting the API"
        return 0
    else
        echo -e "${YELLOW}⚠ Rate limiting may NOT be working${NC}"
        echo "  - No requests were rate limited"
        echo "  - Check rate limiter configuration"
        return 1
    fi
}

# Burst test function
test_burst() {
    echo ""
    echo -e "${YELLOW}Testing burst traffic (rapid requests)...${NC}"
    
    BURST_SIZE=20
    BURST_SUCCESS=0
    BURST_RATE_LIMITED=0
    
    for i in $(seq 1 $BURST_SIZE); do
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/health" 2>/dev/null)
        
        if [ "$HTTP_CODE" == "200" ]; then
            BURST_SUCCESS=$((BURST_SUCCESS + 1))
        elif [ "$HTTP_CODE" == "429" ]; then
            BURST_RATE_LIMITED=$((BURST_RATE_LIMITED + 1))
        fi
        
        # No delay - send as fast as possible
    done
    
    echo ""
    echo "Burst Test Results:"
    echo "  - Sent: $BURST_SIZE rapid requests"
    echo "  - Success: $BURST_SUCCESS"
    echo "  - Rate Limited: $BURST_RATE_LIMITED"
    echo ""
    
    if [ $BURST_RATE_LIMITED -gt 0 ]; then
        echo -e "${GREEN}✓ Burst protection is WORKING${NC}"
    else
        echo -e "${YELLOW}⚠ All burst requests succeeded (may need adjustment)${NC}"
    fi
}

# Test recovery after rate limit
test_recovery() {
    echo ""
    echo -e "${YELLOW}Testing rate limit recovery...${NC}"
    echo "Waiting 60 seconds for rate limit window to reset..."
    
    for i in {60..1}; do
        echo -ne "\rWaiting: ${i}s   "
        sleep 1
    done
    
    echo ""
    echo "Testing if requests work again..."
    
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/health" 2>/dev/null)
    
    if [ "$HTTP_CODE" == "200" ]; then
        echo -e "${GREEN}✓ Rate limit window reset successfully${NC}"
        echo "  - Requests are working again"
    else
        echo -e "${YELLOW}⚠ Request still failing (HTTP $HTTP_CODE)${NC}"
    fi
}

# Check if Prometheus metrics are available
test_prometheus_metrics() {
    echo ""
    echo -e "${YELLOW}Checking Prometheus metrics...${NC}"
    
    # Check if /prometheus endpoint exists
    if curl -s "$BACKEND_URL/prometheus" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Prometheus endpoint is accessible"
        
        # Look for rate limit metrics
        METRICS=$(curl -s "$BACKEND_URL/prometheus")
        
        if echo "$METRICS" | grep -q "rate_limit_exceeded_total"; then
            RATE_LIMIT_COUNT=$(echo "$METRICS" | grep "rate_limit_exceeded_total" | grep -v "#" | awk '{print $2}')
            echo -e "${GREEN}✓${NC} Rate limit metric found: $RATE_LIMIT_COUNT total violations"
        else
            echo -e "${YELLOW}⚠${NC} rate_limit_exceeded_total metric not found"
        fi
        
        if echo "$METRICS" | grep -q "http_requests_total"; then
            echo -e "${GREEN}✓${NC} HTTP request metrics available"
        fi
        
        echo ""
        echo "View full metrics at: $BACKEND_URL/prometheus"
    else
        echo -e "${YELLOW}⚠${NC} Prometheus endpoint not accessible"
        echo "  Metrics may not be exposed in production"
    fi
}

# Main test flow
main() {
    # Check if backend is accessible
    echo "Checking backend availability..."
    if ! curl -s -f "$BACKEND_URL/health" > /dev/null 2>&1; then
        echo -e "${RED}Error: Backend is not accessible at $BACKEND_URL${NC}"
        echo "Make sure the backend is running"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} Backend is accessible"
    echo ""
    
    # Run tests
    test_rate_limit
    RATE_LIMIT_RESULT=$?
    
    test_burst
    
    test_prometheus_metrics
    
    # Optional: Test recovery (takes 60s)
    read -p "Test rate limit recovery? (60s wait) [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        test_recovery
    fi
    
    echo ""
    echo -e "${BLUE}=================================="
    echo "Summary"
    echo "==================================${NC}"
    
    if [ $RATE_LIMIT_RESULT -eq 0 ]; then
        echo -e "${GREEN}✅ Rate limiting is configured correctly${NC}"
        echo ""
        echo "Recommendations:"
        echo "  - Monitor rate_limit_exceeded_total in Prometheus"
        echo "  - Adjust limit in config if needed"
        echo "  - Consider per-user limits for production"
        echo "  - Set up alerts for excessive rate limiting"
    else
        echo -e "${YELLOW}⚠️ Rate limiting may need adjustment${NC}"
        echo ""
        echo "Check:"
        echo "  - Rate limiter is enabled in config"
        echo "  - Middleware is properly configured"
        echo "  - Backend logs for rate limiter messages"
    fi
    
    echo ""
    echo "Configuration File: market_predictor/config.py"
    echo "Current Limit: $RATE_LIMIT requests/minute"
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [BACKEND_URL]"
        echo ""
        echo "Tests API rate limiting (60 requests/minute)"
        echo ""
        echo "Arguments:"
        echo "  BACKEND_URL   Backend URL (default: http://localhost:8000)"
        echo ""
        echo "Examples:"
        echo "  $0                                    # Test localhost"
        echo "  $0 https://your-app.railway.app      # Test production"
        echo ""
        exit 0
        ;;
    *)
        main
        ;;
esac
