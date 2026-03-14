# Infrastructure Setup Verification Script (PowerShell)
# This script verifies that all infrastructure components are properly configured

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Autonomous SME Control Tower" -ForegroundColor Cyan
Write-Host "Infrastructure Verification" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorCount = 0
$WarningCount = 0

function Check-Pass {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Check-Fail {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
    $script:ErrorCount++
}

function Check-Warn {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
    $script:WarningCount++
}

# 1. Check Docker
Write-Host "1. Checking Docker installation..."
try {
    $dockerVersion = docker --version
    Check-Pass "Docker installed: $dockerVersion"
} catch {
    Check-Fail "Docker not found. Please install Docker."
}

# 2. Check Docker Compose
Write-Host ""
Write-Host "2. Checking Docker Compose installation..."
try {
    $composeVersion = docker-compose --version
    Check-Pass "Docker Compose installed: $composeVersion"
} catch {
    Check-Fail "Docker Compose not found. Please install Docker Compose."
}

# 3. Check project structure
Write-Host ""
Write-Host "3. Checking project structure..."

$requiredDirs = @(
    "..\backend\app",
    "..\frontend\app",
    "..\prompts\v1",
    "..\docs"
)

foreach ($dir in $requiredDirs) {
    if (Test-Path $dir) {
        Check-Pass "Directory exists: $dir"
    } else {
        Check-Fail "Directory missing: $dir"
    }
}

# 4. Check required files
Write-Host ""
Write-Host "4. Checking required files..."

$requiredFiles = @(
    "docker-compose.yml",
    "..\backend\Dockerfile",
    "..\backend\requirements.txt",
    "..\backend\app\main.py",
    "..\backend\app\config.py",
    "..\frontend\Dockerfile",
    "..\frontend\package.json",
    "..\.env.example"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Check-Pass "File exists: $file"
    } else {
        Check-Fail "File missing: $file"
    }
}

# 5. Check environment configuration
Write-Host ""
Write-Host "5. Checking environment configuration..."

if (Test-Path "..\.env") {
    Check-Pass ".env file exists"
    
    $envContent = Get-Content "..\.env" -Raw
    $requiredVars = @(
        "AWS_REGION",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "NOVA_LITE_MODEL_ID",
        "SIGNALS_TABLE",
        "DOCUMENTS_BUCKET"
    )
    
    foreach ($var in $requiredVars) {
        if ($envContent -match "^$var=") {
            Check-Pass "Environment variable set: $var"
        } else {
            Check-Warn "Environment variable missing: $var"
        }
    }
} else {
    Check-Warn ".env file not found. Create from .env.example"
    Write-Host "  Run: Copy-Item ..\.env.example ..\.env" -ForegroundColor Yellow
}

# 6. Check backend structure
Write-Host ""
Write-Host "6. Checking backend structure..."

$backendDirs = @(
    "..\backend\app\routers",
    "..\backend\app\agents",
    "..\backend\app\services",
    "..\backend\app\models",
    "..\backend\app\utils"
)

foreach ($dir in $backendDirs) {
    if (Test-Path $dir) {
        Check-Pass "Backend directory exists: $dir"
    } else {
        Check-Fail "Backend directory missing: $dir"
    }
}

# 7. Check AWS service integrations
Write-Host ""
Write-Host "7. Checking AWS service integrations..."

$awsFiles = @(
    "..\backend\app\utils\bedrock_client.py",
    "..\backend\app\services\ddb_service.py",
    "..\backend\app\services\s3_service.py"
)

foreach ($file in $awsFiles) {
    if (Test-Path $file) {
        Check-Pass "AWS service file exists: $file"
        
        $content = Get-Content $file -Raw
        
        if ($content -match "retry_with_backoff") {
            Check-Pass "  - Retry logic implemented"
        } else {
            Check-Warn "  - Retry logic not found"
        }
        
        if ($content -match "CircuitBreaker" -or $content -match "ClientError") {
            Check-Pass "  - Error handling implemented"
        } else {
            Check-Warn "  - Error handling not found"
        }
    } else {
        Check-Fail "AWS service file missing: $file"
    }
}

# 8. Check frontend structure
Write-Host ""
Write-Host "8. Checking frontend structure..."

$frontendDirs = @(
    "..\frontend\app",
    "..\frontend\components",
    "..\frontend\lib"
)

foreach ($dir in $frontendDirs) {
    if (Test-Path $dir) {
        Check-Pass "Frontend directory exists: $dir"
    } else {
        Check-Fail "Frontend directory missing: $dir"
    }
}

# 9. Check frontend configuration
Write-Host ""
Write-Host "9. Checking frontend configuration..."

if (Test-Path "..\frontend\.env.local.example") {
    Check-Pass "Frontend .env.local.example exists"
} else {
    Check-Warn "Frontend .env.local.example not found"
}

if (Test-Path "..\frontend\lib\api.ts") {
    Check-Pass "API client exists"
} else {
    Check-Fail "API client missing"
}

# 10. Validate docker-compose configuration
Write-Host ""
Write-Host "10. Validating docker-compose configuration..."

try {
    $null = docker-compose config 2>&1
    Check-Pass "docker-compose.yml is valid"
} catch {
    Check-Warn "docker-compose.yml validation failed (may need .env file)"
}

# Summary
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Verification Complete" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Errors: $ErrorCount" -ForegroundColor $(if ($ErrorCount -eq 0) { "Green" } else { "Red" })
Write-Host "Warnings: $WarningCount" -ForegroundColor $(if ($WarningCount -eq 0) { "Green" } else { "Yellow" })
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Ensure .env file is configured with AWS credentials"
Write-Host "2. Run: docker-compose up --build"
Write-Host "3. Access backend at http://localhost:8000"
Write-Host "4. Access frontend at http://localhost:3000"
Write-Host ""
