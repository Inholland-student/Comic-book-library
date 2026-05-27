param(
    [Parameter(Position = 0)]
    [ValidateSet("dev", "test", "prod")]
    [string]$Environment = "dev"
)

$ErrorActionPreference = "Stop"

# --- NEW: SECURITY GATE ---
Write-Host "Verification: Running security checks before deployment..." -ForegroundColor Cyan
& "$PSScriptRoot/check-sec.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Deployment aborted due to security vulnerabilities."
    exit 1
}
Write-Host "Security checks passed!" -ForegroundColor Green
# --------------------------

. "$PSScriptRoot/common.ps1"

$Minikube = Get-RequiredCommand "minikube"
$Terraform = Get-RequiredCommand "terraform"
$Kubectl = Get-RequiredCommand "kubectl"

$RootDir = Split-Path -Parent $PSScriptRoot
$TerraformDir = Join-Path $RootDir "terraform"
$Namespace = "comic-library-$Environment"
$TfvarsFile = "envs/$Environment.tfvars"

Write-Host "Checking required tools..."
if (!(Test-Path $Minikube)) { throw "Minikube not found at $Minikube" }
if (!(Test-Path $Terraform)) { throw "Terraform not found at $Terraform" }
if (!(Test-Path $Kubectl)) { throw "kubectl not found at $Kubectl" }

Write-Host "Starting Minikube..."
& $Minikube start

Write-Host "Using Minikube Docker environment..."
& $Minikube docker-env | Invoke-Expression

Write-Host "Building frontend image..."
docker build -t comic-frontend:latest (Join-Path $RootDir "frontend")

Write-Host "Building backend image..."
docker build -t comic-backend:latest -f (Join-Path $RootDir "backend/Dockerfile") $RootDir

Write-Host "Applying Terraform for: $Environment"
Push-Location $TerraformDir
& $Terraform init
$workspaceExists = & $Terraform workspace list | Select-String -Pattern "^\*?\s*$Environment$"
if ($workspaceExists) { & $Terraform workspace select $Environment }
else { & $Terraform workspace new $Environment }
& $Terraform apply "-var-file=$TfvarsFile" -auto-approve
Pop-Location

Write-Host "Restarting app deployments..."
& $Kubectl rollout restart deployment/frontend -n $Namespace
& $Kubectl rollout restart deployment/backend -n $Namespace

Write-Host "Waiting for rollouts..."
& $Kubectl rollout status deployment/frontend -n $Namespace
& $Kubectl rollout status deployment/backend -n $Namespace

Write-Host "`nDeployment finished.`n"
& "$PSScriptRoot/open.ps1" frontend $Environment