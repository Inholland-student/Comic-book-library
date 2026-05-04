param(
    [Parameter(Position = 0)]
    [ValidateSet("dev", "test", "prod")]
    [string]$Environment = "dev"
)

$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $PSScriptRoot
$TerraformDir = Join-Path $RootDir "terraform"
$TfvarsFile = "envs/$Environment.tfvars"

Write-Host "Destroying environment: $Environment"

Push-Location $TerraformDir

terraform workspace select $Environment
terraform destroy -var-file=$TfvarsFile -auto-approve

Pop-Location

Write-Host "Destroyed environment: $Environment"