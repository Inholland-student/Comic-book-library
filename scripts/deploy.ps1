param(
    [Parameter(Position = 0)]
    [ValidateSet("dev", "test", "prod")]
    [string]$Environment = "dev"
)

$ErrorActionPreference = "Stop"

# Full paths, so script does not depend on PATH
$Minikube = "C:\ProgramData\chocolatey\bin\minikube.exe"
$Terraform = "C:\ProgramData\chocolatey\bin\terraform.exe"
$Kubectl = "C:\ProgramData\chocolatey\bin\kubectl.exe"

$RootDir = Split-Path -Parent $PSScriptRoot
$TerraformDir = Join-Path $RootDir "terraform"
$Namespace = "comic-library-$Environment"
$TfvarsFile = "envs/$Environment.tfvars"

Write-Host "Checking required tools..."

if (!(Test-Path $Minikube)) {
    throw "Minikube not found at $Minikube"
}

if (!(Test-Path $Terraform)) {
    throw "Terraform not found at $Terraform"
}

if (!(Test-Path $Kubectl)) {
    throw "kubectl not found at $Kubectl"
}

Write-Host "Starting Minikube..."
& $Minikube start

Write-Host "Using Minikube Docker environment..."
& $Minikube docker-env | Invoke-Expression

Write-Host "Building frontend image..."
docker build -t comic-frontend:latest (Join-Path $RootDir "frontend")

Write-Host "Building backend image..."
docker build -t comic-backend:latest (Join-Path $RootDir "backend")

Write-Host "Applying Terraform for: $Environment"
Push-Location $TerraformDir

& $Terraform init

$workspaceExists = & $Terraform workspace list | Select-String -Pattern "^\*?\s*$Environment$"

if ($workspaceExists) {
    & $Terraform workspace select $Environment
} else {
    & $Terraform workspace new $Environment
}

& $Terraform apply -var-file=$TfvarsFile -auto-approve

Pop-Location

Write-Host "Restarting app deployments..."
& $Kubectl rollout restart deployment/frontend -n $Namespace
& $Kubectl rollout restart deployment/backend -n $Namespace

Write-Host "Waiting for rollouts..."
& $Kubectl rollout status deployment/frontend -n $Namespace
& $Kubectl rollout status deployment/backend -n $Namespace

Write-Host ""
Write-Host "Deployment finished."
Write-Host ""
Write-Host "Check resources:"
Write-Host ".\scripts\status.ps1 $Environment"
Write-Host ""
Write-Host "Open frontend:"
Write-Host "& `"$Minikube`" service frontend-service -n $Namespace"
Write-Host ""
Write-Host "Open phpMyAdmin:"
Write-Host "& `"$Minikube`" service phpmyadmin-service -n $Namespace"