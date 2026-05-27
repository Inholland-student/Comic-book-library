#!/usr/bin/env bash

# ============================================================================
# Generate SBOM (Software Bill of Materials) for Comic Book Library Images
# ============================================================================
# This script generates SBOMs locally using Syft for both frontend and backend
# images. Useful for local development and pre-push verification.
#
# Usage:
#   ./generate-sbom.sh [build|local|all]
#   
#   build   - Build images locally, then generate SBOM
#   local   - Generate SBOM from existing images (comic-frontend:latest, comic-backend:latest)
#   all     - Build, generate SBOM, and show summary (default)
#
# Prerequisites:
#   - Docker or compatible container runtime
#   - Syft: https://github.com/anchore/syft
#
# Install Syft (if not present):
#   curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
# ============================================================================

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SBOM_OUTPUT_DIR="${PROJECT_DIR}/sbom-reports"

# Syft version
SYFT_VERSION="v0.105.0"

# Image names
FRONTEND_IMAGE="comic-frontend:latest"
BACKEND_IMAGE="comic-backend:latest"

# ============================================================================
# Functions
# ============================================================================

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

check_syft() {
    if ! command -v syft &> /dev/null; then
        print_error "Syft not found. Installing..."
        curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | \
            sh -s -- -b /usr/local/bin "$SYFT_VERSION"
        print_success "Syft installed successfully"
    else
        local version=$(syft --version 2>/dev/null || echo "unknown")
        print_success "Syft found: $version"
    fi
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker not found. Please install Docker."
        exit 1
    fi
    print_success "Docker found"
}

build_images() {
    print_header "Building Docker Images"
    
    echo "Building frontend image..."
    docker build -t "$FRONTEND_IMAGE" "$PROJECT_DIR/frontend"
    print_success "Frontend image built: $FRONTEND_IMAGE"
    
    echo "Building backend image..."
    docker build -t "$BACKEND_IMAGE" -f "$PROJECT_DIR/backend/Dockerfile" "$PROJECT_DIR"
    print_success "Backend image built: $BACKEND_IMAGE"
}

generate_sbom() {
    print_header "Generating SBOMs with Syft"
    
    # Create output directory
    mkdir -p "$SBOM_OUTPUT_DIR"
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    
    # ========== Frontend SBOM ==========
    echo "Generating frontend SBOM (CycloneDX)..."
    syft "$FRONTEND_IMAGE" -o cyclonedx-json > "$SBOM_OUTPUT_DIR/frontend-sbom-cyclonedx-${timestamp}.json"
    print_success "Frontend CycloneDX SBOM: $SBOM_OUTPUT_DIR/frontend-sbom-cyclonedx-${timestamp}.json"
    
    echo "Generating frontend SBOM (SPDX)..."
    syft "$FRONTEND_IMAGE" -o spdx-json > "$SBOM_OUTPUT_DIR/frontend-sbom-spdx-${timestamp}.json"
    print_success "Frontend SPDX SBOM: $SBOM_OUTPUT_DIR/frontend-sbom-spdx-${timestamp}.json"
    
    echo "Generating frontend SBOM (table)..."
    syft "$FRONTEND_IMAGE" -o table > "$SBOM_OUTPUT_DIR/frontend-sbom-table-${timestamp}.txt"
    print_success "Frontend table SBOM: $SBOM_OUTPUT_DIR/frontend-sbom-table-${timestamp}.txt"
    
    # ========== Backend SBOM ==========
    echo "Generating backend SBOM (CycloneDX)..."
    syft "$BACKEND_IMAGE" -o cyclonedx-json > "$SBOM_OUTPUT_DIR/backend-sbom-cyclonedx-${timestamp}.json"
    print_success "Backend CycloneDX SBOM: $SBOM_OUTPUT_DIR/backend-sbom-cyclonedx-${timestamp}.json"
    
    echo "Generating backend SBOM (SPDX)..."
    syft "$BACKEND_IMAGE" -o spdx-json > "$SBOM_OUTPUT_DIR/backend-sbom-spdx-${timestamp}.json"
    print_success "Backend SPDX SBOM: $SBOM_OUTPUT_DIR/backend-sbom-spdx-${timestamp}.json"
    
    echo "Generating backend SBOM (table)..."
    syft "$BACKEND_IMAGE" -o table > "$SBOM_OUTPUT_DIR/backend-sbom-table-${timestamp}.txt"
    print_success "Backend table SBOM: $SBOM_OUTPUT_DIR/backend-sbom-table-${timestamp}.txt"
}

show_summary() {
    print_header "SBOM Generation Summary"
    
    echo -e "${GREEN}SBOMs Generated:${NC}"
    ls -lh "$SBOM_OUTPUT_DIR"/ | tail -6
    
    echo ""
    echo -e "${GREEN}Formats:${NC}"
    echo "  • CycloneDX JSON: Machine-readable for dependency tracking"
    echo "  • SPDX JSON: Standard format for license/compliance"
    echo "  • Table: Human-readable summary"
    
    echo ""
    echo -e "${GREEN}Next Steps:${NC}"
    echo "  1. Review SBOMs in: $SBOM_OUTPUT_DIR"
    echo "  2. Use for supply chain security: scan for vulnerabilities"
    echo "  3. Integrate into CI/CD: GitHub Actions workflow included"
    echo ""
    echo -e "${GREEN}Cosign Signing (CI/CD):${NC}"
    echo "  When pushing to registry, SBOMs will be signed with Cosign"
    echo "  Verify with: cosign verify-attestation <image>"
}

# ============================================================================
# Main
# ============================================================================

ACTION="${1:-all}"

echo ""
print_header "Comic Book Library - SBOM Generation"

# Check prerequisites
check_docker
check_syft

case "$ACTION" in
    build)
        build_images
        generate_sbom
        show_summary
        ;;
    local)
        print_warning "Using existing images: $FRONTEND_IMAGE and $BACKEND_IMAGE"
        generate_sbom
        show_summary
        ;;
    all)
        build_images
        generate_sbom
        show_summary
        ;;
    *)
        echo "Invalid action: $ACTION"
        echo ""
        echo "Usage: $0 [build|local|all]"
        echo ""
        echo "  build   - Build images locally, then generate SBOM"
        echo "  local   - Generate SBOM from existing images"
        echo "  all     - Build, generate SBOM, and show summary (default)"
        exit 1
        ;;
esac

echo ""
print_success "Complete!"
