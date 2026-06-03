param(
    [Parameter(Position = 0)]
    [ValidateSet("dev", "test", "prod")]
    [string]$Environment = "dev"
)

$ErrorActionPreference = "Stop"

# --- SECURITY GATE ---
Write-Host "Verification: Running security checks before deployment..." -ForegroundColor Cyan
& "$PSScriptRoot/check-sec.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Deployment aborted due to security vulnerabilities."
    exit 1
}
Write-Host "Security checks passed!" -ForegroundColor Green
# ---------------------

. "$PSScriptRoot/common.ps1"

$Minikube  = Get-RequiredCommand "minikube"
$Terraform = Get-RequiredCommand "terraform"
$Kubectl   = Get-RequiredCommand "kubectl"

$RootDir      = Split-Path -Parent $PSScriptRoot
$TerraformDir = Join-Path $RootDir "terraform"
$Namespace    = "comic-library-$Environment"
$TfvarsFile   = "envs/$Environment.tfvars"

Write-Host "Checking required tools..."
if (!(Test-Path $Minikube))   { throw "Minikube not found at $Minikube" }
if (!(Test-Path $Terraform))  { throw "Terraform not found at $Terraform" }
if (!(Test-Path $Kubectl))    { throw "kubectl not found at $Kubectl" }

Write-Host "Starting Minikube..."
& $Minikube start

Write-Host "Using Minikube Docker environment..."
& $Minikube docker-env | Invoke-Expression

$TfvarsFullPath = Join-Path $TerraformDir $TfvarsFile
$FrontendImageFull   = Get-TfvarsValue -FilePath $TfvarsFullPath -Key "frontend_image"
$BackendImageFull    = Get-TfvarsValue -FilePath $TfvarsFullPath -Key "backend_image"
$MysqlImageFull      = Get-TfvarsValue -FilePath $TfvarsFullPath -Key "mysql_image"
$PhpMyAdminImageFull = Get-TfvarsValue -FilePath $TfvarsFullPath -Key "phpmyadmin_image"

# Strip the @sha256:<digest> suffix before use.
# Docker's -t flag and IfNotPresent lookups only accept name:tag; the digest in
# tfvars is the immutable registry reference used by CI — locally we use plain tags.
$FrontendImageTag   = ($FrontendImageFull   -split '@')[0]
$BackendImageTag    = ($BackendImageFull    -split '@')[0]
$MysqlImageTag      = ($MysqlImageFull      -split '@')[0]
$PhpMyAdminImageTag = ($PhpMyAdminImageFull -split '@')[0]

Write-Host "Building frontend image: $FrontendImageTag..."
docker build -t $FrontendImageTag (Join-Path $RootDir "frontend")

Write-Host "Building backend image: $BackendImageTag..."
docker build -t $BackendImageTag (Join-Path $RootDir "backend")

Write-Host "Deploying Vault to Minikube..."
$VaultManifest = Join-Path $RootDir "kubernetes\vault\vault.yaml"
# Pull third-party images so IfNotPresent can serve them from Minikube's daemon.
docker pull hashicorp/vault:1.21.2
docker pull hashicorp/vault-k8s:1.7.2
docker pull $MysqlImageTag
docker pull $PhpMyAdminImageTag
# Apply manifest: strip placeholder digests and use IfNotPresent for local dev.
(Get-Content $VaultManifest -Raw) `
    -replace '@sha256:[a-f0-9]{64}', '' `
    -replace 'imagePullPolicy: Always', 'imagePullPolicy: IfNotPresent' |
    & $Kubectl apply -f -

Write-Host "Waiting for Vault pod vault-0 to be ready (up to 120s)..."
& $Kubectl wait --for=condition=ready pod/vault-0 -n vault --timeout=120s

Write-Host "Configuring Vault for: $Environment"
& "$PSScriptRoot/setup-vault.ps1" $Environment

Write-Host "Applying Terraform for: $Environment"
Push-Location $TerraformDir
& $Terraform init
$workspaceExists = & $Terraform workspace list | Select-String -Pattern "^\*?\s*$Environment$"
if ($workspaceExists) { & $Terraform workspace select $Environment }
else                  { & $Terraform workspace new  $Environment }

# Override image variables with local (digest-free) tags so Kubernetes references
# the images just built into Minikube's daemon.
# Override image_pull_policy to IfNotPresent so kubelet uses the locally built
# images instead of attempting a registry pull (Always would fail for images
# that only exist in the local Minikube daemon, not in a remote registry).
& $Terraform apply `
    "-var-file=$TfvarsFile" `
    "-var=frontend_image=$FrontendImageTag" `
    "-var=backend_image=$BackendImageTag" `
    "-var=mysql_image=$MysqlImageTag" `
    "-var=phpmyadmin_image=$PhpMyAdminImageTag" `
    "-var=image_pull_policy=IfNotPresent" `
    -auto-approve
Pop-Location

Write-Host "Restarting app deployments..."
& $Kubectl rollout restart deployment/frontend -n $Namespace
& $Kubectl rollout restart deployment/backend  -n $Namespace

Write-Host "Waiting for rollouts..."
& $Kubectl rollout status deployment/frontend -n $Namespace
& $Kubectl rollout status deployment/backend  -n $Namespace

Write-Host "`nDeployment finished.`n"
& "$PSScriptRoot/open.ps1" frontend $Environment
