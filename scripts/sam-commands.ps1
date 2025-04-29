# SAM Commands Helper Script for PowerShell

# Get the project root directory (one level up from the scripts directory)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

# Default project prefix - can be overridden with -ProjectPrefix parameter
$ProjectPrefix = "wfg-clients"
$ProjectPrefixCamel = "WFGClients"

function Build-SAM {
    Write-Host "Building SAM application..." -ForegroundColor Cyan
    Push-Location $projectRoot
    sam build
    Pop-Location
}

function Invoke-ApiFunction {
    Write-Host "Invoking API function locally..." -ForegroundColor Cyan
    Push-Location $projectRoot
    sam local invoke ApiFunction --skip-pull-image
    Pop-Location
}

function Invoke-EventFunction {
    Write-Host "Invoking Event function locally..." -ForegroundColor Cyan
    Push-Location $projectRoot
    sam local invoke EventFunction -e events/event.json --skip-pull-image
    Pop-Location
}

function Start-LocalApi {
    Write-Host "Starting local API Gateway..." -ForegroundColor Cyan
    Push-Location $projectRoot
    sam local start-api --skip-pull-image
    Pop-Location
}

function Deploy-SAM {
    param (
        [string]$ProjectPrefix = $script:ProjectPrefix,
        [string]$ProjectPrefixCamel = $script:ProjectPrefixCamel
    )

    Write-Host "Deploying SAM application with prefix: $ProjectPrefix..." -ForegroundColor Cyan
    
    # First deploy the IAM role
    Write-Host "Deploying IAM role..." -ForegroundColor Yellow
    Push-Location $projectRoot
    aws cloudformation deploy `
        --template-file iam-role.yaml `
        --stack-name "$ProjectPrefix-iam" `
        --capabilities CAPABILITY_IAM `
        --parameter-overrides "ProjectPrefix=$ProjectPrefixCamel" "ProjectPrefixLower=$ProjectPrefix" `
        --no-fail-on-empty-changeset
    
    # Get AWS account ID
    $awsAccount = aws sts get-caller-identity --query "Account" --output text
    $awsRegion = aws configure get region
    
    # Create ECR repository if it doesn't exist
    Write-Host "Creating/verifying ECR repository..." -ForegroundColor Yellow
    $repoExists = aws ecr describe-repositories --repository-names "$ProjectPrefix" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Creating ECR repository: $ProjectPrefix" -ForegroundColor Green
        aws ecr create-repository --repository-name "$ProjectPrefix"
    }
    else {
        Write-Host "ECR repository already exists: $ProjectPrefix" -ForegroundColor Green
    }
    
    # ECR repository URI
    $ecrUri = "${awsAccount}.dkr.ecr.${awsRegion}.amazonaws.com"
    
    # Then deploy the SAM application
    Write-Host "Deploying SAM application..." -ForegroundColor Yellow
    sam deploy --stack-name "$ProjectPrefix" `
        --no-confirm-changeset `
        --no-fail-on-empty-changeset `
        --capabilities CAPABILITY_IAM `
        --parameter-overrides "ProjectPrefix=$ProjectPrefixCamel" `
        --image-repository "${ecrUri}/$ProjectPrefix"
    Pop-Location
}

function Remove-DockerResources {
    Write-Host "Cleaning Docker images and containers..." -ForegroundColor Cyan
    docker system prune -f
}

function Show-Help {
    Write-Host "SAM Commands Helper" -ForegroundColor Green
    Write-Host "===================" -ForegroundColor Green
    Write-Host "Available commands:" -ForegroundColor Green
    Write-Host "  build       - Build the SAM application" -ForegroundColor White
    Write-Host "  invoke-api  - Invoke the API function locally" -ForegroundColor White
    Write-Host "  invoke-event - Invoke the Event function locally" -ForegroundColor White
    Write-Host "  start-api   - Start a local API Gateway" -ForegroundColor White
    Write-Host "  deploy      - Deploy the SAM application to AWS" -ForegroundColor White
    Write-Host "                Optional parameters:" -ForegroundColor White
    Write-Host "                -ProjectPrefix <prefix>  - Prefix for resources (default: wfg-clients)" -ForegroundColor White
    Write-Host "                -ProjectPrefixCamel <prefix> - CamelCase prefix (default: WFGClients)" -ForegroundColor White
    Write-Host "  clean-docker - Clean Docker images and containers" -ForegroundColor White
    Write-Host "  help        - Show this help message" -ForegroundColor White
}

# Process command line arguments
if ($args.Count -eq 0) {
    Show-Help
    exit
}

# Check for project prefix parameter
for ($i = 0; $i -lt $args.Count; $i++) {
    if ($args[$i] -eq "-ProjectPrefix" -and $i+1 -lt $args.Count) {
        $ProjectPrefix = $args[$i+1]
    }
    if ($args[$i] -eq "-ProjectPrefixCamel" -and $i+1 -lt $args.Count) {
        $ProjectPrefixCamel = $args[$i+1]
    }
}

switch ($args[0]) {
    "build" { Build-SAM }
    "invoke-api" { Invoke-ApiFunction }
    "invoke-event" { Invoke-EventFunction }
    "start-api" { Start-LocalApi }
    "deploy" { Deploy-SAM -ProjectPrefix $ProjectPrefix -ProjectPrefixCamel $ProjectPrefixCamel }
    "clean-docker" { Remove-DockerResources }
    "help" { Show-Help }
    default { 
        Write-Host "Unknown command: $($args[0])" -ForegroundColor Red
        Show-Help
    }
}
