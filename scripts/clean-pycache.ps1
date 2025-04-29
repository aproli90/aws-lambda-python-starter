# Set environment variable to prevent Python from creating bytecode files
$env:PYTHONDONTWRITEBYTECODE = 1

# Get the project root directory (one level up from the scripts directory)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

# Find and remove __pycache__ directories only in application code folders (excluding .venv)
Write-Host "Removing __pycache__ directories from application code folders..." -ForegroundColor Cyan

# Get all __pycache__ directories
$pycacheDirs = Get-ChildItem -Path $projectRoot -Filter "__pycache__" -Directory -Recurse | 
    Where-Object { $_.FullName -notlike "*.venv*" }

if ($pycacheDirs.Count -eq 0) {
    Write-Host "No __pycache__ directories found in application code folders." -ForegroundColor Green
} else {
    $pycacheDirs | ForEach-Object {
        Write-Host "Removing: $($_.FullName)" -ForegroundColor Yellow
        Remove-Item -Path $_.FullName -Recurse -Force
    }
    Write-Host "`nRemoved $($pycacheDirs.Count) __pycache__ directories from application code folders!" -ForegroundColor Green
}

Write-Host "`nThe PYTHONDONTWRITEBYTECODE environment variable has been set for this session." -ForegroundColor Green
Write-Host "`nNote: To permanently disable bytecode generation, you can:" -ForegroundColor Cyan
Write-Host "1. Add 'sys.dont_write_bytecode = True' at the top of your main Python scripts" -ForegroundColor Cyan
Write-Host "2. Add 'export PYTHONDONTWRITEBYTECODE=1' to your PowerShell profile" -ForegroundColor Cyan
