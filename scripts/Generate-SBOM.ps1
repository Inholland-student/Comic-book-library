#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Generate SBOM (Software Bill of Materials) for Comic Book Library images using Syft.

.DESCRIPTION
    This script generates SBOMs locally for both frontend and backend Docker images.
    Supports multiple formats: CycloneDX JSON, SPDX JSON, and human-readable table.
    Useful for local development and pre-push verification.

.PARAMETER Action
    Build, Local, or All (default)
    - build: Build images locally, then generate SBOM
    - local: Generate SBOM from existing images (comic-frontend:latest, comic-backend:latest)
    - all:   Build, generate SBOM, and show summary

.EXAMPLE
    .\Generate-SBOM.ps1
    .\Generate-SBOM.ps1 -Action build
    .\Generate-SBOM.ps1 -Action local

.NOTES
    Prerequisites:
    - Docker or compatible container runtime
    - Syft: https://github.com/anchore/syft
    
    Install Syft on Windows:
    choco install syft  # if using Chocolatey
    
    Or download from: https://github.com/anchore/syft/releases
#>

param(
    [ValidateSet("build", "local", "all")]
    [string]$Action = "all"
)

$ErrorActionPreference = "Stop"

# ============================================================================
# Configuration
# ============================================================================

$SYFT_VERSION = "v0.105.0"
$FRONTEND_IMAGE = "comic-frontend:latest"
$BACKEND_IMAGE = "comic-backend:latest"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
$SbomOutputDir = Join-Path $ProjectDir "sbom-reports"

# ============================================================================
# Functions
# ============================================================================

function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Blue
    Write-Host $Text -ForegroundColor Blue
    Write-Host "==========================================" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Text)
    Write-Host "✓ $Text" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Text)
    Write-Host "⚠ $Text" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param([string]$Text)
    Write-Host "✗ $Text" -ForegroundColor Red
}

function Test-Syft {
    <#
    Check if Syft is installed and available
    #>
    try {
        $version = & syft --version 2>&1
        Write-Success "Syft found: $version"
        return $true
    }
    catch {
        Write-Error-Custom "Syft not found in PATH"
        Write-Host ""
        Write-Host "Install Syft:"
        Write-Host "  Option 1 - Chocolatey: choco install syft"
        Write-Host "  Option 2 - Download: https://github.com/anchore/syft/releases"
        Write-Host "  Option 3 - Manual: curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | pwsh"
        return $false
    }
}

function Test-Docker {
    <#
    Check if Docker is installed and running
    #>
    try {
        $result = & docker info 2>&1
        Write-Success "Docker is running"
        return $true
    }
    catch {
        Write-Error-Custom "Docker not found or not running"
        return $false
    }
}

function Build-Images {
    Write-Header "Building Docker Images"
    
    Write-Host "Building frontend image..."
    & docker build -t $FRONTEND_IMAGE "$ProjectDir\frontend"
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Frontend image built: $FRONTEND_IMAGE"
    }
    else {
        throw "Frontend image build failed"
    }
    
    Write-Host "Building backend image..."
    & docker build -t $BACKEND_IMAGE -f "$ProjectDir\backend\Dockerfile" $ProjectDir
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Backend image built: $BACKEND_IMAGE"
    }
    else {
        throw "Backend image build failed"
    }
}

function Generate-SBOM {
    Write-Header "Generating SBOMs with Syft"
    
    # Create output directory
    if (!(Test-Path $SbomOutputDir)) {
        New-Item -ItemType Directory -Path $SbomOutputDir -Force | Out-Null
    }
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    
    # ========== Frontend SBOM ==========
    Write-Host "Generating frontend SBOM (CycloneDX)..."
    & syft "$FRONTEND_IMAGE" -o cyclonedx-json | Out-File "$SbomOutputDir\frontend-sbom-cyclonedx-${timestamp}.json"
    Write-Success "Frontend CycloneDX SBOM: frontend-sbom-cyclonedx-${timestamp}.json"
    
    Write-Host "Generating frontend SBOM (SPDX)..."
    & syft "$FRONTEND_IMAGE" -o spdx-json | Out-File "$SbomOutputDir\frontend-sbom-spdx-${timestamp}.json"
    Write-Success "Frontend SPDX SBOM: frontend-sbom-spdx-${timestamp}.json"
    
    Write-Host "Generating frontend SBOM (table)..."
    & syft "$FRONTEND_IMAGE" -o table | Out-File "$SbomOutputDir\frontend-sbom-table-${timestamp}.txt"
    Write-Success "Frontend table SBOM: frontend-sbom-table-${timestamp}.txt"
    
    # ========== Backend SBOM ==========
    Write-Host "Generating backend SBOM (CycloneDX)..."
    & syft "$BACKEND_IMAGE" -o cyclonedx-json | Out-File "$SbomOutputDir\backend-sbom-cyclonedx-${timestamp}.json"
    Write-Success "Backend CycloneDX SBOM: backend-sbom-cyclonedx-${timestamp}.json"
    
    Write-Host "Generating backend SBOM (SPDX)..."
    & syft "$BACKEND_IMAGE" -o spdx-json | Out-File "$SbomOutputDir\backend-sbom-spdx-${timestamp}.json"
    Write-Success "Backend SPDX SBOM: backend-sbom-spdx-${timestamp}.json"
    
    Write-Host "Generating backend SBOM (table)..."
    & syft "$BACKEND_IMAGE" -o table | Out-File "$SbomOutputDir\backend-sbom-table-${timestamp}.txt"
    Write-Success "Backend table SBOM: backend-sbom-table-${timestamp}.txt"
}

function Show-Summary {
    Write-Header "SBOM Generation Summary"
    
    Write-Host ""
    Write-Host "SBOMs Generated:" -ForegroundColor Green
    Get-ChildItem $SbomOutputDir -File | Select-Object -Last 6 | ForEach-Object {
        Write-Host "  $(Get-Date $_.LastWriteTime -Format 'yyyy-MM-dd HH:mm:ss')  $($_.Name)  ($([math]::Round($_.Length/1KB, 2)) KB)"
    }
    
    Write-Host ""
    Write-Host "Formats:" -ForegroundColor Green
    Write-Host "  • CycloneDX JSON: Machine-readable for dependency tracking"
    Write-Host "  • SPDX JSON: Standard format for license/compliance"
    Write-Host "  • Table: Human-readable summary"
    
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Green
    Write-Host "  1. Review SBOMs: $SbomOutputDir"
    Write-Host "  2. Use for supply chain security: scan for vulnerabilities"
    Write-Host "  3. Integrate into CI/CD: Push to Git, GitHub Actions handles signing"
    
    Write-Host ""
    Write-Host "Cosign Signing (CI/CD):" -ForegroundColor Green
    Write-Host "  When pushing to registry, SBOMs will be signed with Cosign"
    Write-Host "  Verify with: cosign verify-attestation <image>"
}

# ============================================================================
# Main
# ============================================================================

Write-Header "Comic Book Library - SBOM Generation"

# Check prerequisites
if (!(Test-Docker)) {
    exit 1
}

if (!(Test-Syft)) {
    exit 1
}

switch ($Action) {
    "build" {
        Build-Images
        Generate-SBOM
        Show-Summary
    }
    "local" {
        Write-Warning "Using existing images: $FRONTEND_IMAGE and $BACKEND_IMAGE"
        Generate-SBOM
        Show-Summary
    }
    "all" {
        Build-Images
        Generate-SBOM
        Show-Summary
    }
}

Write-Host ""
Write-Success "Complete!"
