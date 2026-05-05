param(
    [Parameter(Position = 0)]
    [ValidateSet("frontend", "phpmyadmin")]
    [string]$Service = "frontend",

    [Parameter(Position = 1)]
    [ValidateSet("dev", "test", "prod")]
    [string]$Environment = "dev"
)

$ErrorActionPreference = "Stop"

. "$PSScriptRoot/common.ps1"

$Minikube = Get-RequiredCommand "minikube"
$Namespace = "comic-library-$Environment"

if ($Service -eq "frontend") {
    Write-Host "Opening frontend for $Environment..."
    & $Minikube service frontend-service -n $Namespace
}
else {
    Write-Host "Opening phpMyAdmin for $Environment..."
    & $Minikube service phpmyadmin-service -n $Namespace
}