# SAM local testing script for Lambda functions
# This script uses SAM CLI to build and invoke Lambda functions locally

# Get the project root directory (one level up from the scripts directory)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

# Event file paths - these are used in the script
$API_HELLO_EVENT = Join-Path $projectRoot "events/api-hello.json"
$API_HEALTH_EVENT = Join-Path $projectRoot "events/api-health.json"
$EVENT_DAILY_PROCESSING = Join-Path $projectRoot "events/event-daily-processing.json"
$EVENT_DATA_SYNC = Join-Path $projectRoot "events/event-data-sync.json"

# Function to run SAM local invoke
function Invoke-SamFunction {
    param (
        [string]$FunctionName,
        [string]$EventFile,
        [string]$Description
    )
    
    Write-Host "`n========== Testing $($FunctionName): $($Description) ==========" -ForegroundColor Cyan
    
    # Check if the event file exists
    if (-not (Test-Path -Path $EventFile)) {
        Write-Host "Error: Event file $($EventFile) not found!" -ForegroundColor Red
        return
    }
    
    # Invoke the function locally
    Write-Host "Invoking $($FunctionName) locally with event from $($EventFile)..." -ForegroundColor Yellow
    
    # Use sam local invoke with the --debug flag to see more information
    # Change to project root directory before running sam commands
    Push-Location $projectRoot
    sam local invoke $FunctionName -e $EventFile --debug --profile "default"
    Pop-Location
    
    Write-Host "Test completed for $($FunctionName): $($Description)." -ForegroundColor Green
}

# Main execution
Write-Host "Starting SAM local testing..." -ForegroundColor Cyan

# Build the functions using SAM with --use-container flag
Write-Host "Building Lambda functions with SAM..." -ForegroundColor Yellow
Push-Location $projectRoot
sam build --use-container
Pop-Location

# Run tests for all functions and endpoints
Write-Host "`nRunning tests for all functions..." -ForegroundColor Yellow

# Test API functions
Invoke-SamFunction -FunctionName "ApiFunction" -EventFile $API_HELLO_EVENT -Description "Hello Endpoint"
# Invoke-SamFunction -FunctionName "ApiFunction" -EventFile $API_HEALTH_EVENT -Description "Health Endpoint"

# Test Event functions
Invoke-SamFunction -FunctionName "EventFunction" -EventFile $EVENT_DAILY_PROCESSING -Description "Daily Processing"
# Invoke-SamFunction -FunctionName "EventFunction" -EventFile $EVENT_DATA_SYNC -Description "Data Sync"

Write-Host "`nAll tests completed." -ForegroundColor Green
Write-Host "`nIf SAM local invoke is not working, you can use the local_test.py script instead:" -ForegroundColor Yellow
Write-Host "python scripts/local_test.py" -ForegroundColor Yellow
