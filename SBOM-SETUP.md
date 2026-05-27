# SBOM Generation & Cosign Signing Setup Guide

## Overview

This guide explains how to integrate Software Bill of Materials (SBOM) generation and Cosign signing into your CI/CD pipeline. The setup uses:

- **Syft**: Generates SBOMs in multiple formats (CycloneDX, SPDX)
- **Cosign**: Signs and attaches SBOMs to container images using keyless signing (Sigstore)
- **GitHub Actions**: Automates the entire workflow

## Quick Start

### 1. Local Development (Generate SBOM locally)

#### Option A: PowerShell (Windows)
```powershell
cd .\scripts
.\Generate-SBOM.ps1 all    # Build images and generate SBOM
.\Generate-SBOM.ps1 local  # Use existing images
```

#### Option B: Bash (Linux/macOS)
```bash
cd scripts
chmod +x generate-sbom.sh
./generate-sbom.sh all    # Build images and generate SBOM
./generate-sbom.sh local  # Use existing images
```

**Output**: SBOMs saved to `./sbom-reports/`

### 2. CI/CD Pipeline (GitHub Actions)

The GitHub Actions workflow automatically:
1. Builds Docker images for frontend & backend
2. Pushes to container registry (configurable)
3. Generates SBOMs using Syft
4. Signs SBOMs with Cosign (keyless via Sigstore)
5. Verifies attestations

**Workflow file**: `.github/workflows/sbom-cosign.yml`

## Prerequisites

### For Local Development

#### Windows (PowerShell)
```powershell
# Install Syft via Chocolatey
choco install syft

# Or download manually from: https://github.com/anchore/syft/releases
```

#### Linux/macOS
```bash
# Install Syft
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin

# Verify installation
syft --version
```

#### All Platforms
- Docker or Docker Desktop
- Bash or PowerShell (for scripts)

### For GitHub Actions

- GitHub Actions enabled in your repository
- Push access to container registry (see Configuration below)

## Configuration

### 1. Registry Setup

The workflow supports multiple container registries. Configure by setting environment variables in `.github/workflows/sbom-cosign.yml`:

#### Option A: GitHub Container Registry (GHCR) - **Recommended**
```yaml
env:
  REGISTRY: ghcr.io
  REGISTRY_USERNAME: ${{ github.actor }}
  REGISTRY_PASSWORD: ${{ secrets.GITHUB_TOKEN }}
```

**No additional setup needed!** GitHub automatically provides `GITHUB_TOKEN` for GHCR access.

#### Option B: Docker Hub
1. Create Docker Hub account & token
2. Add GitHub Secrets:
   - `REGISTRY_USERNAME`: Your Docker Hub username
   - `REGISTRY_PASSWORD`: Your Docker Hub personal access token
3. Update `.github/workflows/sbom-cosign.yml`:
   ```yaml
   env:
     REGISTRY: docker.io
     REGISTRY_USERNAME: ${{ secrets.REGISTRY_USERNAME }}
     REGISTRY_PASSWORD: ${{ secrets.REGISTRY_PASSWORD }}
   ```

#### Option C: Private Registry
1. Get registry credentials
2. Add GitHub Secrets for credentials
3. Update `.github/workflows/sbom-cosign.yml` with your registry URL

### 2. GitHub Secrets Setup

For Docker Hub or private registries:

1. Go to: **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Add secrets:
   - `REGISTRY_USERNAME`: Your registry username
   - `REGISTRY_PASSWORD`: Your registry password/token

### 3. Container Image Names

Update the workflow if you want to customize image names:

```yaml
env:
  FRONTEND_IMAGE_NAME: ${{ github.repository }}/frontend
  BACKEND_IMAGE_NAME: ${{ github.repository }}/backend
```

This creates images like:
- `ghcr.io/meryamdouiri/comic-book-library/frontend:latest`
- `ghcr.io/meryamdouiri/comic-book-library/backend:latest`

## How It Works

### Workflow Steps

```
┌─────────────────────────────────────────────────────────────┐
│ 1. BUILD JOB                                                │
├─────────────────────────────────────────────────────────────┤
│ • Checkout code                                             │
│ • Login to registry (GHCR, Docker Hub, etc.)                │
│ • Build frontend image → Push to registry                   │
│ • Build backend image → Push to registry                    │
│ • Export image digests for signing                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. SBOM JOB (runs after BUILD)                              │
├─────────────────────────────────────────────────────────────┤
│ • Install Syft                                              │
│ • Generate SBOM for frontend (CycloneDX + SPDX)             │
│ • Generate SBOM for backend (CycloneDX + SPDX)              │
│ • Upload SBOM files as artifacts                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. COSIGN ATTEST JOB (runs after SBOM)                      │
├─────────────────────────────────────────────────────────────┤
│ • Install Cosign                                            │
│ • Download SBOM files                                       │
│ • Sign & attach SBOMs using Cosign keyless signing          │
│   (Fulcio + Rekor via OIDC)                                 │
│ • Attestations attached to image digest                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. VERIFY JOB (runs after COSIGN ATTEST)                    │
├─────────────────────────────────────────────────────────────┤
│ • Verify CycloneDX attestation for frontend                 │
│ • Verify SPDX attestation for frontend                      │
│ • Verify CycloneDX attestation for backend                  │
│ • Verify SPDX attestation for backend                       │
│ • Display summary                                           │
└─────────────────────────────────────────────────────────────┘
```

### Keyless Signing (Sigstore)

The workflow uses **Cosign's keyless signing** with Sigstore:

1. **No private keys to manage** ✓
2. **OIDC token** from GitHub Actions
3. **Fulcio** issues short-lived certificates
4. **Rekor** provides transparency log
5. **Attestations verified via public key** from Sigstore's transparency log

Benefits:
- No credential rotation needed
- Transparent and auditable
- Works across teams
- Industry standard

## Usage

### Trigger the Workflow

Push to `main` or `develop` branch:
```bash
git push origin main
```

Or manually trigger:
1. Go to **Actions** tab
2. Select **Build, SBOM, and Cosign Sign**
3. Click **Run workflow**

### Check Workflow Status

1. Go to **Actions** tab
2. View job logs for each step
3. Download SBOM artifacts

### Verify Signatures Locally

Once images are pushed, verify signatures locally:

```bash
# Install Cosign
curl -sSfL https://github.com/sigstore/cosign/releases/download/v2.2.2/cosign-linux-amd64 -o cosign
chmod +x cosign

# Verify CycloneDX attestation
cosign verify-attestation \
  --type cyclonedx \
  ghcr.io/meryamdouiri/comic-book-library/frontend:latest

# Verify SPDX attestation
cosign verify-attestation \
  --type spdx \
  ghcr.io/meryamdouiri/comic-book-library/backend:latest

# Get attestation as JSON
cosign verify-attestation \
  --type cyclonedx \
  ghcr.io/meryamdouiri/comic-book-library/frontend:latest | jq .
```

### Download SBOMs

From GitHub Actions:
1. Go to **Actions** → **Build, SBOM, and Cosign Sign** (latest run)
2. Scroll down to **Artifacts**
3. Download **sbom-files**

Or via API:
```bash
# List artifacts
gh run list --workflow sbom-cosign.yml --limit 1

# Download artifacts
gh run download <RUN_ID> -n sbom-files
```

## SBOM Formats

### 1. CycloneDX JSON
- **Format**: JSON
- **Use case**: Dependency tracking, license compliance
- **Tools**: Tools that support CycloneDX (many SCA tools)
- **File**: `frontend-sbom-cyclonedx.json`

Example:
```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.4",
  "components": [
    {
      "type": "library",
      "name": "vue",
      "version": "3.x.x",
      "purl": "pkg:npm/vue@3.x.x"
    }
  ]
}
```

### 2. SPDX JSON
- **Format**: JSON (SPDX specification)
- **Use case**: License tracking, regulatory compliance (SBOM Act)
- **Tools**: SPDX-compliant tools
- **File**: `frontend-sbom-spdx.json`

Example:
```json
{
  "spdxVersion": "SPDX-2.3",
  "creationInfo": {
    "created": "2024-01-01T00:00:00Z"
  },
  "packages": [
    {
      "name": "vue",
      "SPDXID": "SPDXRef-Package-vue"
    }
  ]
}
```

### 3. Table Format (Local Only)
- **Format**: Human-readable text table
- **Use case**: Quick review, debugging
- **File**: `frontend-sbom-table-YYYYMMDD_HHMMSS.txt`

## Security Considerations

### 1. Image Signing with Digests
- Images signed using **digest** (SHA256), not tags
- Tags can change, digests are immutable
- Ensures you verify the exact image you intended

### 2. Keyless Signing
- No private keys stored in repositories
- Uses GitHub's OIDC token + Sigstore
- Transparent via Rekor transparency log
- Auditable and secure

### 3. Attestation Types
- **CycloneDX**: For dependency management
- **SPDX**: For compliance & regulatory requirements
- Both formats provide supply chain visibility

### 4. Verification
- Verify attestations after pulling images
- Use `cosign verify-attestation` in deployment scripts
- Block deployment if attestation verification fails

## Troubleshooting

### Issue: "No files found" when generating SBOM locally

**Solution**: Ensure Docker images are built first:
```powershell
.\Generate-SBOM.ps1 build    # Builds before generating
```

### Issue: "Registry login failed" in GitHub Actions

**Solution**: Check GitHub Secrets:
1. For GHCR: Ensure `GITHUB_TOKEN` is available (automatic)
2. For Docker Hub: Verify `REGISTRY_USERNAME` and `REGISTRY_PASSWORD` secrets
3. For private registry: Verify credentials and registry URL

### Issue: "Cosign not found" error

**Solution**: The workflow installs Cosign automatically. If running locally:
```bash
# Install Cosign
curl -sSfL https://github.com/sigstore/cosign/releases/download/v2.2.2/cosign-linux-amd64 -o cosign
chmod +x cosign
sudo mv cosign /usr/local/bin/
```

### Issue: Attestation verification fails

**Solution**: Ensure image digest is used (not tag):
```bash
# Wrong (uses tag):
cosign verify-attestation ghcr.io/owner/repo/image:latest

# Correct (uses digest):
cosign verify-attestation ghcr.io/owner/repo/image@sha256:abc123...
```

## Integration with Deployment

### Kubernetes Deployment with SBOM Verification

Add a policy to verify attestations before deploying:

```yaml
# Example: Kyverno policy
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-attestations
spec:
  validationFailureAction: audit
  rules:
    - name: verify-sbom-attestation
      match:
        resources:
          kinds:
            - Pod
      verifyImages:
        - imageReferences:
            - "ghcr.io/meryamdouiri/*"
          attestations:
            - name: cyclonedx-sbom
              attestationFormat: cyclonedx
```

### Supply Chain Security Scanning

After verifying attestation, scan the SBOM:

```bash
# Get attestation
cosign verify-attestation \
  --type cyclonedx \
  ghcr.io/meryamdouiri/comic-book-library/frontend:$SHA | \
  jq .payload -r | base64 -d > frontend-sbom.json

# Scan for vulnerabilities (example with Grype)
grype sbom:frontend-sbom.json --fail-on high
```

## File Locations

```
.
├── .github/
│   └── workflows/
│       └── sbom-cosign.yml              ← GitHub Actions workflow
├── backend/
│   └── Dockerfile                       ← Updated with metadata labels
├── frontend/
│   └── Dockerfile                       ← Updated with metadata labels
├── scripts/
│   ├── Generate-SBOM.ps1                ← PowerShell SBOM generation
│   └── generate-sbom.sh                 ← Bash SBOM generation
└── sbom-reports/                        ← Generated SBOMs (local)
    ├── frontend-sbom-cyclonedx-*.json
    ├── frontend-sbom-spdx-*.json
    ├── backend-sbom-cyclonedx-*.json
    └── backend-sbom-spdx-*.json
```

## References

- **Syft**: https://github.com/anchore/syft
- **Cosign**: https://github.com/sigstore/cosign
- **Sigstore**: https://www.sigstore.dev/
- **CycloneDX**: https://cyclonedx.org/
- **SPDX**: https://spdx.dev/
- **GitHub Actions**: https://docs.github.com/en/actions

## Next Steps

1. **Push to GitHub**: `git push` to trigger workflow
2. **Monitor build**: Check Actions tab for job logs
3. **Download SBOMs**: Get artifacts from workflow run
4. **Verify locally**: Use `cosign verify-attestation`
5. **Integrate into deployment**: Add policy checks before deploying

## Support

For issues:
1. Check workflow logs in GitHub Actions
2. Review error messages carefully
3. Verify registry credentials
4. Check Cosign documentation: https://github.com/sigstore/cosign
