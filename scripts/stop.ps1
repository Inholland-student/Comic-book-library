$ErrorActionPreference = "Stop"

. "$PSScriptRoot/common.ps1"

$Minikube = Get-RequiredCommand "minikube"

if (!(Test-Path $Minikube)) {
    throw "Minikube not found at $Minikube"
}

Write-Host "Stopping Minikube..."
& $Minikube stop

Write-Host "Minikube stopped."