# GitHub Actions Setup: SBOM & Cosign Signing

## Quick Reference

| Component | Purpose | Status |
|-----------|---------|--------|
| Syft | Generate SBOM (CycloneDX, SPDX) | ✅ Included |
| Cosign | Sign & attach attestations | ✅ Included |
| Sigstore | Keyless signing infrastructure | ✅ Auto (no config) |
| GitHub OIDC | OIDC token for keyless signing | ✅ Auto (no config) |

## 1. Initial Setup (One Time)

### Step 1: Verify GitHub Actions is Enabled

1. Go to **Settings → Actions → General**
2. Ensure **Actions permissions** is set to "Allow all actions"
3. Click **Save**

### Step 2: Enable OIDC for Cosign Keyless Signing

GitHub Actions automatically provides OIDC tokens for keyless signing. **No additional setup required!**

The workflow uses:
- `id-token: write` permission (already in workflow)
- Environment variable: `COSIGN_EXPERIMENTAL=1` (already set)

### Step 3: Configure Container Registry

#### Option A: GitHub Container Registry (GHCR) - **Recommended, No Setup Needed**
- Uses `GITHUB_TOKEN` automatically provided by GitHub Actions
- No secrets to configure
- Images pushed to: `ghcr.io/meryamdouiri/comic-book-library/...`

#### Option B: Docker Hub (Optional)
1. Create Docker Hub account
2. Generate personal access token (Settings → Security → New Access Token)
3. Go to **Settings → Secrets and variables → Actions**
4. Click **New repository secret**
5. Add secrets:
   - Name: `REGISTRY_USERNAME`
   - Value: Your Docker Hub username
   - Name: `REGISTRY_PASSWORD`
   - Value: Your Docker Hub personal access token

6. Update `.github/workflows/sbom-cosign.yml`:
   ```yaml
   env:
     REGISTRY: docker.io
     REGISTRY_USERNAME: ${{ secrets.REGISTRY_USERNAME }}
     REGISTRY_PASSWORD: ${{ secrets.REGISTRY_PASSWORD }}
   ```

#### Option C: Private Registry (Optional)
Follow the same steps as Option B, replacing:
- Registry URL: `registry.company.com` (your registry)
- Update `env.REGISTRY` in workflow

## 2. Workflow Overview

### File Location
`.github/workflows/sbom-cosign.yml`

### Workflow Diagram

```
TRIGGER: Push to main/develop or Manual Run
           ↓
    ┌──────────────────┐
    │  BUILD JOB       │
    │  Builds images & │
    │  pushes to       │
    │  registry        │
    └──────────────────┘
           ↓
    ┌──────────────────┐
    │  SBOM JOB        │
    │  Generates       │
    │  CycloneDX &     │
    │  SPDX SBOMs      │
    └──────────────────┘
           ↓
    ┌──────────────────┐
    │ COSIGN ATTEST    │
    │  Signs & attaches│
    │  SBOMs to images │
    │  using Sigstore  │
    └──────────────────┘
           ↓
    ┌──────────────────┐
    │ VERIFY JOB       │
    │ Verifies         │
    │ attestations are │
    │ correctly signed │
    └──────────────────┘
           ↓
         DONE ✓
```

### Jobs Explanation

#### 1. BUILD Job
- **Purpose**: Build Docker images and push to registry
- **Outputs**: Image digests (needed for signing)
- **Permissions**: 
  - `contents: read` - Read repository code
  - `packages: write` - Push to registry
  - `id-token: write` - OIDC for Cosign

#### 2. SBOM Job
- **Purpose**: Generate SBOMs using Syft
- **Outputs**: 
  - `frontend-sbom-cyclonedx.json`
  - `frontend-sbom-spdx.json`
  - `backend-sbom-cyclonedx.json`
  - `backend-sbom-spdx.json`
- **Artifacts**: SBOMs available for download (90 day retention)

#### 3. COSIGN ATTEST Job
- **Purpose**: Sign SBOMs and attach to images
- **Process**:
  1. Download SBOM files
  2. Use `cosign attest` with image digest
  3. Sign using Sigstore keyless (OIDC token)
  4. Attestation stored in registry (OCI Artifact)
- **Permissions**: `id-token: write` for Sigstore signing

#### 4. VERIFY Job
- **Purpose**: Verify signed attestations
- **Process**:
  1. Use `cosign verify-attestation`
  2. Check CycloneDX & SPDX attestations
  3. Confirm all signatures are valid
- **Result**: Job fails if verification fails (safety check)

## 3. How Keyless Signing Works

### Traditional Signing (What We Avoid)
```
⚠ Store private key in secrets (risky)
⚠ Manual key rotation required
⚠ Difficult to audit who signed what
```

### Keyless Signing with Sigstore (What We Use)
```
1. GitHub Actions provides OIDC token
   ↓
2. Cosign sends token to Fulcio (CA)
   ↓
3. Fulcio verifies token, issues short-lived cert
   ↓
4. Cosign signs attestation with cert
   ↓
5. Attestation + signature → Rekor (transparency log)
   ↓
6. Anyone can verify using Sigstore's public key
   ↓
7. Signature logged in transparency log (auditable)

No private keys stored anywhere! ✓
```

## 4. Running the Workflow

### Automatic Trigger
Push code to `main` or `develop` branch:
```bash
git add .
git commit -m "Add feature"
git push origin main
```

### Manual Trigger
1. Go to **Actions** tab in GitHub
2. Select **Build, SBOM, and Cosign Sign**
3. Click **Run workflow**
4. (Optional) Select branch
5. Click **Run workflow**

### Monitor Progress
1. Go to **Actions** tab
2. Click latest run
3. View job status and logs in real-time

## 5. Accessing Results

### SBOM Artifacts

From GitHub UI:
1. Go to **Actions** → Latest run
2. Scroll to **Artifacts** section
3. Download **sbom-files**

From command line:
```bash
# List recent runs
gh run list --workflow sbom-cosign.yml

# Download artifacts from latest run
gh run download --name sbom-files
```

### Container Image

Images are pushed to registry:
- **GHCR**: `ghcr.io/meryamdouiri/comic-book-library/frontend:latest`
- **Docker Hub** (if configured): `docker.io/username/frontend:latest`

List images:
```bash
# GHCR
gh api /user/packages | jq '.[] | .name'

# Docker Hub
curl -s https://hub.docker.com/v2/repositories/username/ | jq '.results[].name'
```

## 6. Verifying Attestations Locally

After workflow completes, verify signatures from your machine:

### Install Cosign (if not already installed)
```bash
# Linux/macOS
curl -sSfL https://github.com/sigstore/cosign/releases/download/v2.2.2/cosign-linux-amd64 -o cosign
chmod +x cosign
sudo mv cosign /usr/local/bin/

# Or download from: https://github.com/sigstore/cosign/releases
```

### Verify Attestations
```bash
# Set environment variable for keyless verification
export COSIGN_EXPERIMENTAL=1

# Verify frontend CycloneDX attestation
cosign verify-attestation \
  --type cyclonedx \
  ghcr.io/meryamdouiri/comic-book-library/frontend:latest

# Verify backend SPDX attestation
cosign verify-attestation \
  --type spdx \
  ghcr.io/meryamdouiri/comic-book-library/backend:latest

# Show attestation payload
cosign verify-attestation \
  --type cyclonedx \
  ghcr.io/meryamdouiri/comic-book-library/frontend:latest | jq -r '.payload | @base64d | fromjson'
```

### Understanding Verification Output

```
✓ Attestation successfully verified!

Certificate verified from Sigstore's roots
│
├─ Authority: Sigstore OIDC issuer
├─ Issuer: https://token.actions.githubusercontent.com (GitHub)
└─ Subject: https://github.com/meryamdouiri/Comic-book-library

Attestation is signed by GitHub Actions OIDC token
```

## 7. Workflow Customization

### Change Trigger Branches
Edit `.github/workflows/sbom-cosign.yml`:
```yaml
on:
  push:
    branches:
      - main        # Change these
      - develop
```

### Change Image Tags
Edit workflow `env` section:
```yaml
env:
  FRONTEND_IMAGE_NAME: custom/frontend
  BACKEND_IMAGE_NAME: custom/backend
```

### Change Tool Versions
Edit workflow `env` section:
```yaml
env:
  SYFT_VERSION: v0.100.0     # Update if needed
  COSIGN_VERSION: v2.0.0     # Update if needed
```

### Skip Verification Job
Comment out the verification job if needed:
```yaml
# verify-attestation:
#   runs-on: ubuntu-latest
#   ...
```

## 8. Troubleshooting

### Issue: Workflow fails at BUILD job

**Error**: `Login failed for registry`
- **Fix**: Check GitHub Secrets (for Docker Hub) or GHCR token availability
- **Check**: Settings → Secrets and variables → Actions

**Error**: `Permission denied: image push`
- **Fix**: Verify registry credentials have push permissions
- **Check**: Docker Hub/registry user permissions

### Issue: Workflow fails at SBOM job

**Error**: `Syft not found`
- **Fix**: The workflow auto-installs Syft, but check internet connection
- **Check**: Workflow logs for network errors

**Error**: `Image not found`
- **Fix**: BUILD job may have failed, check BUILD job logs first

### Issue: Workflow fails at COSIGN ATTEST job

**Error**: `cosign: command not found`
- **Fix**: The workflow auto-installs Cosign, but check internet
- **Check**: Workflow logs for download errors

**Error**: `COSIGN_EXPERIMENTAL not enabled`
- **Fix**: Verify `id-token: write` permission in workflow
- **Check**: The workflow already has this, but verify not overridden

**Error**: `Failed to get OIDC token`
- **Fix**: Ensure GitHub Actions has proper permissions
- **Check**: Settings → Actions → General → Workflow permissions

### Issue: Verification fails

**Error**: `Failed to verify attestation`
- **Likely cause**: Image was not signed by Cosign in that run
- **Fix**: Re-run the workflow
- **Check**: Workflow COSIGN ATTEST job completed successfully

**Error**: `Certificate validation failed`
- **Likely cause**: Using wrong image digest or tag changed
- **Fix**: Use exact image digest from build job, not tag
- **Example**:
  ```bash
  # Wrong (tag may have changed):
  cosign verify-attestation ghcr.io/owner/repo:latest
  
  # Correct (exact digest):
  cosign verify-attestation ghcr.io/owner/repo@sha256:abc123...
  ```

## 9. Security Best Practices

### 1. Always Use Image Digests
```bash
# ✗ Bad: Tag can change
docker pull ghcr.io/owner/repo:latest

# ✓ Good: Digest is immutable
docker pull ghcr.io/owner/repo@sha256:abc123def456...
```

### 2. Verify Attestations Before Deployment
```bash
# Verify in deployment script
cosign verify-attestation --type cyclonedx <image> || exit 1
docker run <image>
```

### 3. Keep SBOM Records
- Download and archive SBOMs for compliance
- Audit trail of all dependencies
- License tracking

### 4. Monitor Transparency Log
- Attestations logged in Rekor (transparent)
- Can be audited: https://rekor.tlog.dev/
- Provides transparency and trust

### 5. Integrate with Supply Chain Security
- Scan SBOMs for vulnerabilities (Grype, etc.)
- Enforce policies on dependencies
- Track license compliance

## 10. Next Steps

1. ✅ Verify workflow runs (push to main/develop)
2. ✅ Download SBOMs from artifacts
3. ✅ Verify attestations locally
4. ✅ Integrate into deployment pipeline
5. ✅ Set up automated SBOM scanning
6. ✅ Document dependencies and compliance

## References

- **Workflow file**: `.github/workflows/sbom-cosign.yml`
- **Setup guide**: `SBOM-SETUP.md`
- **Syft documentation**: https://github.com/anchore/syft
- **Cosign documentation**: https://github.com/sigstore/cosign
- **Sigstore**: https://www.sigstore.dev/
- **GitHub Actions OIDC**: https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect
