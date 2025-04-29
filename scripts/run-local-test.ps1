# PowerShell wrapper for local_test.py
# This script makes it easier to run the local_test.py script with different options

param (
    [Parameter(Mandatory=$false)]
    [ValidateSet("api", "event", "all")]
    [string]$Function = "all",
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("api-hello", "api-health", "event-daily-processing", "event-data-sync")]
    [string]$Event,
    
    [switch]$Help
)

# Display help information
if ($Help) {
    Write-Host "Usage: .\run-local-test.ps1 [-Function <api|event|all>] [-Event <event-name>] [-Help]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Function <api|event|all>    Specify which function type to test (default: all)"
    Write-Host "  -Event <event-name>          Test with a specific event file"
    Write-Host "  -Help                        Display this help message"
    Write-Host ""
    Write-Host "Available events:"
    Write-Host "  api-hello                    API Gateway event for /hello endpoint"
    Write-Host "  api-health                   API Gateway event for /health endpoint"
    Write-Host "  event-daily-processing       CloudWatch event for DailyProcessing"
    Write-Host "  event-data-sync              CloudWatch event for DataSync"
    Write-Host ""
    exit 0
}

# Build the command arguments
$pythonArgs = @()
if ($Function -ne "all") {
    $pythonArgs += "--function"
    $pythonArgs += $Function
}
if ($Event) {
    $pythonArgs += "--event"
    $pythonArgs += $Event
}

# Run the Python script
Write-Host "Running local Lambda tests..." -ForegroundColor Cyan
$argString = $pythonArgs -join " "
Write-Host "Command: python scripts/local_test.py $argString" -ForegroundColor Yellow
& python scripts/local_test.py $pythonArgs

# Check the exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host "Tests completed successfully." -ForegroundColor Green
} else {
    Write-Host "Tests failed with exit code $LASTEXITCODE." -ForegroundColor Red
}
