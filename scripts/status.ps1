param(
    [Parameter(Position = 0)]
    [ValidateSet("dev", "test", "prod")]
    [string]$Environment = "dev"
)

$ErrorActionPreference = "Stop"

. "$PSScriptRoot/common.ps1"

$Kubectl = Get-RequiredCommand "kubectl"
$Namespace = "comic-library-$Environment"

if (!(Test-Path $Kubectl)) {
    throw "kubectl not found at $Kubectl"
}

Write-Host "Namespace: $Namespace"
Write-Host ""

Write-Host "Pods:"
& $Kubectl get pods -n $Namespace

Write-Host ""
Write-Host "Deployments:"
& $Kubectl get deployments -n $Namespace

Write-Host ""
Write-Host "Services:"
& $Kubectl get services -n $Namespace