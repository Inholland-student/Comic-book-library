# Quick Start Checklist

Complete this checklist to get your SBOM + Cosign pipeline up and running.

## Phase 1: Initial Setup (5 minutes)

### [ ] Step 1: Verify GitHub Actions
- [ ] Go to Settings → Actions → General
- [ ] Ensure "Allow all actions" is selected
- [ ] Click Save

### [ ] Step 2: Enable OIDC (Already Done!)
- ✅ GitHub Actions automatically provides OIDC tokens
- ✅ Keyless signing is preconfigured in the workflow

### [ ] Step 3: Configure Registry

Choose one option:

#### Option A: GitHub Container Registry (GHCR) - **RECOMMENDED**
- ✅ No setup needed!
- ✅ Images will go to: `ghcr.io/meryamdouiri/comic-book-library/...`
- ✅ Uses automatic `GITHUB_TOKEN`


## Phase 2: First Run (2 minutes)

### [ ] Step 4: Commit and Push

```bash
git add -A
git commit -m "Add SBOM generation and Cosign signing"
git push origin main
```

### [ ] Step 5: Monitor Workflow

- [ ] Go to GitHub → **Actions** tab
- [ ] Click **Build, SBOM, and Cosign Sign**
- [ ] Watch jobs run:
  - BUILD (2-3 min) ✓
  - SBOM (1-2 min) ✓
  - COSIGN ATTEST (1-2 min) ✓
  - VERIFY (30 sec) ✓

### [ ] Step 6: Download SBOMs

- [ ] Go to latest workflow run
- [ ] Scroll to **Artifacts**
- [ ] Download **sbom-files**
- [ ] Extract to review:
  - `frontend-sbom-cyclonedx.json`
  - `frontend-sbom-spdx.json`
  - `backend-sbom-cyclonedx.json`
  - `backend-sbom-spdx.json`

## Phase 3: Local Development (5 minutes)

### [ ] Step 7: Install Syft Locally

#### Windows (Chocolatey)
```powershell
choco install syft
```

#### Windows (Manual)
- [ ] Download from: https://github.com/anchore/syft/releases
- [ ] Extract and add to PATH

#### Linux/macOS
```bash
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
```

### [ ] Step 8: Generate SBOMs Locally

#### PowerShell
```powershell
cd .\scripts
.\Generate-SBOM.ps1 all
```

#### Bash
```bash
cd scripts
./generate-sbom.sh all
```

- [ ] SBOMs saved to `./sbom-reports/`
- [ ] Review table format: `sbom-reports/frontend-sbom-table-*.txt`

## Phase 4: Verification (3 minutes)

### [ ] Step 9: Install Cosign

```bash
# Linux/macOS
curl -sSfL https://github.com/sigstore/cosign/releases/download/v2.2.2/cosign-linux-amd64 -o cosign
chmod +x cosign
sudo mv cosign /usr/local/bin/

# Windows (download from GitHub releases)
```

### [ ] Step 10: Verify Attestations

```bash
export COSIGN_EXPERIMENTAL=1

cosign verify-attestation \
  --type cyclonedx \
  ghcr.io/meryamdouiri/comic-book-library/frontend:latest
```

Expected output:
```
✓ Attestation successfully verified!
```

## Phase 5: Integration (Optional)

### [ ] Step 11: Integrate with Deployment

Add attestation verification to your deployment script:

```bash
# Verify before deploying
cosign verify-attestation --type cyclonedx <image> || exit 1
kubectl apply -f deployment.yaml
```

### [ ] Step 12: Set Up Vulnerability Scanning

```bash
# Install Grype
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin

# Scan SBOM
grype sbom:sbom-reports/backend-sbom-cyclonedx-*.json --fail-on high
```

## Documentation Reference

| Document | When to Read |
|----------|--------------|
| [IMPLEMENTATION-SUMMARY.md](./IMPLEMENTATION-SUMMARY.md) | Overview of what was added |
| [SBOM-SETUP.md](./SBOM-SETUP.md) | Complete setup & concepts |
| [GITHUB-ACTIONS-SETUP.md](./GITHUB-ACTIONS-SETUP.md) | GitHub Actions details |
| [LOCAL-DEVELOPMENT-SBOM.md](./LOCAL-DEVELOPMENT-SBOM.md) | Local development workflow |

## Troubleshooting Quick Links

- **Workflow fails**: See [GITHUB-ACTIONS-SETUP.md](./GITHUB-ACTIONS-SETUP.md#8-troubleshooting)
- **Syft not found**: See [LOCAL-DEVELOPMENT-SBOM.md](./LOCAL-DEVELOPMENT-SBOM.md#error-syft-not-found)
- **Verification fails**: See [GITHUB-ACTIONS-SETUP.md](./GITHUB-ACTIONS-SETUP.md#issue-verification-fails)
- **Registry login fails**: See [GITHUB-ACTIONS-SETUP.md](./GITHUB-ACTIONS-SETUP.md#issue-workflow-fails-at-build-job)

## Success Checklist

- ✅ Workflow triggered on push
- ✅ Images built and pushed to registry
- ✅ SBOMs generated in multiple formats
- ✅ Attestations signed with Cosign
- ✅ Signatures verified automatically
- ✅ SBOMs downloaded and reviewed
- ✅ Attestations verified locally
- ✅ Documentation reviewed

## What You Now Have

```
✅ Automated SBOM generation (CI/CD)
✅ Keyless image signing (Sigstore)
✅ Local development workflow
✅ Enterprise supply chain security
✅ Comprehensive documentation
✅ Industry-standard formats (CycloneDX, SPDX)
✅ Transparent & auditable signatures
✅ Regulatory compliance ready
```

## Next Steps After Setup

1. Review SBOMs from first workflow run
2. Integrate SBOM verification into deployment
3. Set up vulnerability scanning with Grype
4. Monitor attestations in Rekor (transparency log)
5. Document compliance requirements
6. Train team on SBOM verification

## Need Help?

1. Check the documentation files (4 comprehensive guides included)
2. Review workflow logs in GitHub Actions
3. Check tool documentation:
   - Syft: https://github.com/anchore/syft
   - Cosign: https://github.com/sigstore/cosign
   - Sigstore: https://www.sigstore.dev/

---

**You're ready to go! Start with Phase 1, Step 1.** 🚀
