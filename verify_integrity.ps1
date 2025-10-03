# Audiobook Integrity Verification Runner (PowerShell)
# This script runs the verification tool inside the Docker container

param(
    [switch]$Verbose,
    [switch]$Quick,
    [switch]$OrphansOnly,
    [switch]$Fix,
    [switch]$DryRun,
    [switch]$Help
)

$ContainerName = "audiobookDownloader"

if ($Help) {
    Write-Host "Audiobook Integrity Verification Tool" -ForegroundColor Green
    Write-Host "======================================"
    Write-Host ""
    Write-Host "Usage: .\verify_integrity.ps1 [options]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Verbose      Show detailed output for each file"
    Write-Host "  -Quick        Skip ffprobe verification (faster)"
    Write-Host "  -OrphansOnly  Only check for orphaned files"
    Write-Host "  -Fix          Automatically fix issues found"
    Write-Host "  -DryRun       Show what would be fixed without making changes"
    Write-Host "  -Help         Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\verify_integrity.ps1                    # Basic verification"
    Write-Host "  .\verify_integrity.ps1 -Verbose           # Detailed output"
    Write-Host "  .\verify_integrity.ps1 -Quick             # Fast check"
    Write-Host "  .\verify_integrity.ps1 -OrphansOnly       # Check orphaned files only"
    Write-Host "  .\verify_integrity.ps1 -DryRun -Fix       # Preview fixes"
    Write-Host "  .\verify_integrity.ps1 -Fix               # Apply fixes automatically"
    exit 0
}

# Check if container is running
$containerStatus = docker ps --format "table {{.Names}}" | Select-String "^${ContainerName}$"
if (-not $containerStatus) {
    Write-Host "❌ Container '${ContainerName}' is not running." -ForegroundColor Red
    Write-Host "Please start the container first." -ForegroundColor Yellow
    exit 1
}

Write-Host "🔍 Running audiobook integrity verification..." -ForegroundColor Green
Write-Host "Container: ${ContainerName}" -ForegroundColor Cyan
Write-Host ""

# Build arguments
$args = @()
if ($Verbose) { $args += "--verbose" }
if ($Quick) { $args += "--quick" }
if ($OrphansOnly) { $args += "--orphans-only" }
if ($Fix) { $args += "--fix" }
if ($DryRun) { $args += "--dry-run" }

# Run the verification script inside the container
$command = "python /app/verify_integrity.py " + ($args -join " ")
docker exec -it $ContainerName sh -c $command