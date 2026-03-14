#!/bin/bash

# Infrastructure Setup Verification Script
# This script verifies that all infrastructure components are properly configured

set -e

echo "=========================================="
echo "Autonomous SME Control Tower"
echo "Infrastructure Verification"
echo "=========================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check functions
check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# 1. Check Docker
echo "1. Checking Docker installation..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    check_pass "Docker installed: $DOCKER_VERSION"
else
    check_fail "Docker not found. Please install Docker."
    exit 1
fi

# 2. Check Docker Compose
echo ""
echo "2. Checking Docker Compose installation..."
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    check_pass "Docker Compose installed: $COMPOSE_VERSION"
else
    check_fail "Docker Compose not found. Please install Docker Compose."
    exit 1
fi

# 3. Check project structure
echo ""
echo "3. Checking project structure..."

REQUIRED_DIRS=(
    "../backend/app"
    "../frontend/app"
    "../prompts/v1"
    "../docs"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        check_pass "Directory exists: $dir"
    else
        check_fail "Directory missing: $dir"
    fi
done

# 4. Check required files
echo ""
echo "4. Checking required files..."

REQUIRED_FILES=(
    "docker-compose.yml"
    "../backend/Dockerfile"
    "../backend/requirements.txt"
    "../backend/app/main.py"
    "../backend/app/config.py"
    "../frontend/Dockerfile"
    "../frontend/package.json"
    "../.env.example"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        check_pass "File exists: $file"
    else
        check_fail "File missing: $file"
    fi
done

# 5. Check environment configuration
echo ""
echo "5. Checking environment configuration..."

if [ -f "../.env" ]; then
    check_pass ".env file exists"
    
    # Check for required variables
    REQUIRED_VARS=(
        "AWS_REGION"
        "AWS_ACCESS_KEY_ID"
        "AWS_SECRET_ACCESS_KEY"
        "NOVA_LITE_MODEL_ID"
        "SIGNALS_TABLE"
        "DOCUMENTS_BUCKET"
    )
    
    for var in "${REQUIRED_VARS[@]}"; do
        if grep -q "^${var}=" ../.env; then
            check_pass "Environment variable set: $var"
        else
            check_warn "Environment variable missing: $var"
        fi
    done
else
    check_warn ".env file not found. Create from .env.example"
    echo "  Run: cp ../.env.example ../.env"
fi

# 6. Check backend structure
echo ""
echo "6. Checking backend structure..."

BACKEND_DIRS=(
    "../backend/app/routers"
    "../backend/app/agents"
    "../backend/app/services"
    "../backend/app/models"
    "../backend/app/utils"
)

for dir in "${BACKEND_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        check_pass "Backend directory exists: $dir"
    else
        check_fail "Backend directory missing: $dir"
    fi
done

# 7. Check AWS service integrations
echo ""
echo "7. Checking AWS service integrations..."

AWS_FILES=(
    "../backend/app/utils/bedrock_client.py"
    "../backend/app/services/ddb_service.py"
    "../backend/app/services/s3_service.py"
)

for file in "${AWS_FILES[@]}"; do
    if [ -f "$file" ]; then
        check_pass "AWS service file exists: $file"
        
        # Check for error handling patterns
        if grep -q "retry_with_backoff" "$file"; then
            check_pass "  - Retry logic implemented"
        else
            check_warn "  - Retry logic not found"
        fi
        
        if grep -q "CircuitBreaker" "$file" || grep -q "ClientError" "$file"; then
            check_pass "  - Error handling implemented"
        else
            check_warn "  - Error handling not found"
        fi
    else
        check_fail "AWS service file missing: $file"
    fi
done

# 8. Check frontend structure
echo ""
echo "8. Checking frontend structure..."

FRONTEND_DIRS=(
    "../frontend/app"
    "../frontend/components"
    "../frontend/lib"
)

for dir in "${FRONTEND_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        check_pass "Frontend directory exists: $dir"
    else
        check_fail "Frontend directory missing: $dir"
    fi
done

# 9. Check frontend configuration
echo ""
echo "9. Checking frontend configuration..."

if [ -f "../frontend/.env.local.example" ]; then
    check_pass "Frontend .env.local.example exists"
else
    check_warn "Frontend .env.local.example not found"
fi

if [ -f "../frontend/lib/api.ts" ]; then
    check_pass "API client exists"
else
    check_fail "API client missing"
fi

# 10. Validate docker-compose configuration
echo ""
echo "10. Validating docker-compose configuration..."

if docker-compose config > /dev/null 2>&1; then
    check_pass "docker-compose.yml is valid"
else
    check_warn "docker-compose.yml validation failed (may need .env file)"
fi

# Summary
echo ""
echo "=========================================="
echo "Verification Complete"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Ensure .env file is configured with AWS credentials"
echo "2. Run: docker-compose up --build"
echo "3. Access backend at http://localhost:8000"
echo "4. Access frontend at http://localhost:3000"
echo ""
