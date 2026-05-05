param(
    [Parameter(Position = 0)]
    [ValidateSet("dev", "test", "prod")]
    [string]$Environment = "dev"
)

$ErrorActionPreference = "Stop"

. "$PSScriptRoot/common.ps1"

$Terraform = Get-RequiredCommand "terraform"

$RootDir = Split-Path -Parent $PSScriptRoot
$TerraformDir = Join-Path $RootDir "terraform"
$TfvarsFile = "envs/$Environment.tfvars"

if (!(Test-Path $Terraform)) {
    throw "Terraform not found at $Terraform"
}

Write-Host "Destroying environment: $Environment"

Push-Location $TerraformDir

& $Terraform workspace select $Environment
& $Terraform destroy "-var-file=$TfvarsFile" -auto-approve

Pop-Location

Write-Host "Destroyed environment: $Environment"