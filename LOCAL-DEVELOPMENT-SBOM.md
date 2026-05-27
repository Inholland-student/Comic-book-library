# Local Development: SBOM & Cosign Guide

This guide explains how to work with SBOMs during local development.

## Quick Start

### 1. Generate SBOM Locally (Windows/PowerShell)

```powershell
# Navigate to scripts directory
cd .\scripts

# Generate SBOM (builds images first)
.\Generate-SBOM.ps1 all

# Or use existing images without rebuilding
.\Generate-SBOM.ps1 local
```

### 2. Generate SBOM Locally (Linux/macOS/Bash)

```bash
cd scripts
chmod +x generate-sbom.sh
./generate-sbom.sh all    # Build and generate
./generate-sbom.sh local  # Use existing images
```

### 3. Find Generated SBOMs

```
comic-book-library/
└── sbom-reports/
    ├── frontend-sbom-cyclonedx-YYYYMMDD_HHMMSS.json
    ├── frontend-sbom-spdx-YYYYMMDD_HHMMSS.json
    ├── frontend-sbom-table-YYYYMMDD_HHMMSS.txt
    ├── backend-sbom-cyclonedx-YYYYMMDD_HHMMSS.json
    ├── backend-sbom-spdx-YYYYMMDD_HHMMSS.json
    └── backend-sbom-table-YYYYMMDD_HHMMSS.txt
```

## Installation Prerequisites

### Windows (PowerShell)

#### 1. Install Syft via Chocolatey

```powershell
# If Chocolatey is installed
choco install syft

# Verify installation
syft --version
```

#### 2. Manual Installation (if Chocolatey not available)

a. Download from GitHub:
   - Go to: https://github.com/anchore/syft/releases
   - Download: `syft_0.105.0_windows_amd64.zip` (or latest)
   
b. Extract and add to PATH:
   - Extract zip to `C:\Program Files\Syft`
   - Add `C:\Program Files\Syft` to PATH
   
c. Verify:
   ```powershell
   syft --version
   ```

### Linux/macOS (Bash)

```bash
# Install Syft
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | \
  sh -s -- -b /usr/local/bin

# Verify
syft --version
```

### All Platforms

- **Docker**: Must be installed and running
  - Windows: [Docker Desktop](https://www.docker.com/products/docker-desktop)
  - Linux: `sudo apt install docker.io` or similar
  - macOS: [Docker Desktop](https://www.docker.com/products/docker-desktop)

## Workflow: From Code to SBOM

### 1. Make Code Changes

```bash
# Example: update dependencies
cd backend
pip install new-package
pip freeze > requirements.txt
```

### 2. Generate SBOM Locally

```powershell
# PowerShell
.\scripts\Generate-SBOM.ps1 build
```

```bash
# Bash
./scripts/generate-sbom.sh build
```

This will:
- Build fresh Docker images
- Generate SBOMs in multiple formats
- Save to `./sbom-reports/`

### 3. Review SBOM Changes

```bash
# Compare SBOMs
diff sbom-reports/frontend-sbom-*.json

# View in JSON viewer/IDE
code sbom-reports/frontend-sbom-cyclonedx-*.json
```

### 4. Check for Vulnerabilities

```bash
# Install Grype (vulnerability scanner)
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin

# Scan SBOM
grype sbom:sbom-reports/backend-sbom-cyclonedx-*.json --fail-on high
```

### 5. Commit and Push

```bash
git add sbom-reports/     # Optional: commit SBOM snapshots
git commit -m "Update dependencies, verify SBOM"
git push origin feature-branch
```

GitHub Actions will:
- Build official images
- Generate fresh SBOMs
- Sign with Cosign
- Verify attestations

## Understanding SBOM Files

### CycloneDX Format

**File**: `frontend-sbom-cyclonedx-*.json`

**Used for**: Dependency tracking, license compliance

**Content**:
```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.4",
  "components": [
    {
      "type": "library",
      "name": "vue",
      "version": "3.3.4",
      "purl": "pkg:npm/vue@3.3.4",
      "licenses": [
        {
          "license": {
            "name": "MIT"
          }
        }
      ]
    }
  ]
}
```

**Useful for**:
- Importing into SCA tools (Sonatype, etc.)
- License compliance checking
- Dependency tracking
- Vulnerability scanning

### SPDX Format

**File**: `frontend-sbom-spdx-*.json`

**Used for**: Regulatory compliance (SBOM Act), standardized reporting

**Content**:
```json
{
  "spdxVersion": "SPDX-2.3",
  "creationInfo": {
    "created": "2024-01-01T00:00:00Z",
    "creators": ["Tool: syft-0.105.0"]
  },
  "packages": [
    {
      "name": "vue",
      "SPDXID": "SPDXRef-Package-vue",
      "downloadLocation": "https://registry.npmjs.org/vue/-/vue-3.3.4.tgz",
      "filesAnalyzed": false
    }
  ]
}
```

**Useful for**:
- Government/regulatory requirements
- SBOM Act compliance (US Executive Order)
- Open source audits
- Standardized exchange

### Table Format

**File**: `frontend-sbom-table-*.txt`

**Used for**: Quick human review

**Content**:
```
 NAME                                       VERSION         TYPE
 @vue/reactivity-transform                  3.3.4           npm
 @vue/server-renderer                       3.3.4           npm
 @vueuse/core                               10.7.2          npm
 axios                                      1.6.7           npm
 chalk                                      5.3.0           npm
 csstype                                    3.1.2           npm
 ...
```

**Useful for**:
- Quick review of components
- Manual inspection
- Debugging

## Common Tasks

### Find a Specific Package in SBOM

```bash
# CycloneDX JSON
grep -A5 '"name": "vue"' sbom-reports/frontend-sbom-cyclonedx-*.json

# SPDX JSON
grep -A5 '"name": "vue"' sbom-reports/frontend-sbom-spdx-*.json

# Table format
grep vue sbom-reports/frontend-sbom-table-*.txt
```

### Check License of a Dependency

```bash
# Using jq (install with: choco install jq or apt install jq)
cat sbom-reports/frontend-sbom-cyclonedx-*.json | jq '.components[] | select(.name=="vue") | .licenses'
```

### Export SBOM to Different Format

```bash
# Already have the formats, but can regenerate specific format
syft comic-frontend:latest -o cyclonedx-json > my-sbom.json
syft comic-frontend:latest -o spdx-json > my-sbom-spdx.json
syft comic-frontend:latest -o table > my-sbom.txt
syft comic-frontend:latest -o json > my-sbom-syft.json
```

### Verify Image Before Push

```bash
# Generate SBOM
.\scripts\Generate-SBOM.ps1 local

# Scan for vulnerabilities
grype comic-frontend:latest --fail-on high

# Only push if scan passes
docker push ghcr.io/meryamdouiri/comic-book-library/frontend:latest
```

## Testing SBOM in CI/CD Before Push

1. **Generate SBOM locally**
   ```powershell
   .\scripts\Generate-SBOM.ps1 build
   ```

2. **Review quality**
   ```powershell
   # Check SBOM file sizes (should be >1KB)
   Get-ChildItem .\sbom-reports\ | Format-Table Name, Length
   ```

3. **Test scanning locally** (optional)
   ```bash
   grype sbom:sbom-reports/backend-sbom-cyclonedx-*.json
   ```

4. **Review table format**
   ```powershell
   Get-Content .\sbom-reports\frontend-sbom-table-*.txt | Out-Host -Paging
   ```

5. **Then push to trigger GitHub Actions**
   ```bash
   git push origin main
   ```

## Integrating SBOM into Development Workflow

### Pre-commit Hook (Optional)

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash

# Generate fresh SBOM before commit
echo "Generating SBOM..."
./scripts/generate-sbom.sh local

# Scan for high-severity vulnerabilities
echo "Scanning for vulnerabilities..."
grype sbom:sbom-reports/backend-sbom-cyclonedx-*.json --fail-on high || exit 1

echo "✓ SBOM checks passed, proceeding with commit"
```

### CI/CD Integration (GitHub Actions)

Already integrated! See `.github/workflows/sbom-cosign.yml`

## Troubleshooting

### Error: "Syft not found"

**Windows (PowerShell)**:
```powershell
# Check if installed
syft --version

# If not, install via Chocolatey
choco install syft

# Or download from: https://github.com/anchore/syft/releases
```

**Linux/macOS**:
```bash
# Install
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin

# Check
syft --version
```

### Error: "Docker is not running"

**Windows**:
- Open Docker Desktop application
- Wait for Docker to start
- Try again

**Linux**:
```bash
sudo systemctl start docker
```

### Error: "Image not found: comic-frontend:latest"

**Solution**: Build images first

```powershell
# PowerShell
.\scripts\Generate-SBOM.ps1 build
```

```bash
# Bash
./scripts/generate-sbom.sh build
```

### Error: "Permission denied" (Linux/macOS)

```bash
# Make script executable
chmod +x ./scripts/generate-sbom.sh

# Try again
./scripts/generate-sbom.sh build
```

## Performance Tips

### 1. Cache Docker Layers

```bash
# Build caches intermediate layers automatically
# First build: ~2-3 minutes
# Subsequent builds: ~30 seconds (if code unchanged)
```

### 2. Skip SBOM Generation if Unchanged

```powershell
# If only documentation changed, skip SBOM generation
.\scripts\Generate-SBOM.ps1 local   # Use existing images
```

### 3. Generate Only One Format

```bash
# If you only need CycloneDX
syft comic-frontend:latest -o cyclonedx-json > frontend-sbom-cyclonedx.json
```

## Security Considerations

### 1. Review Dependencies Regularly

```bash
# Keep SBOM in version control (optional)
git add sbom-reports/
git commit -m "Update SBOM with dependency review"
```

### 2. Scan for Vulnerabilities

```bash
# Use Grype before committing changes to dependencies
grype sbom:sbom-reports/backend-sbom-cyclonedx-*.json
```

### 3. Monitor License Compliance

```bash
# Review licenses in SBOM
jq '.components[].licenses' sbom-reports/frontend-sbom-cyclonedx-*.json
```

### 4. Verify Signatures (After Push)

After pushing to GitHub and workflow completes:

```bash
# Install Cosign
curl -sSfL https://github.com/sigstore/cosign/releases/download/v2.2.2/cosign-linux-amd64 -o cosign
chmod +x cosign

# Verify attestations
COSIGN_EXPERIMENTAL=1 cosign verify-attestation \
  --type cyclonedx \
  ghcr.io/meryamdouiri/comic-book-library/frontend:latest
```

## Next Steps

1. ✅ Generate SBOM locally
2. ✅ Review formats
3. ✅ Push to GitHub (triggers CI/CD)
4. ✅ Download signed SBOMs from GitHub Actions
5. ✅ Verify signatures locally
6. ✅ Integrate SBOM verification into deployment

## References

- **Syft**: https://github.com/anchore/syft
- **Grype**: https://github.com/anchore/grype
- **Cosign**: https://github.com/sigstore/cosign
- **CycloneDX**: https://cyclonedx.org/
- **SPDX**: https://spdx.dev/
