param(
    [Parameter(Position = 0)]
    [ValidateSet("dev", "test", "prod")]
    [string]$Environment = "dev"
)

$Namespace = "comic-library-$Environment"

Write-Host "Namespace: $Namespace"
Write-Host ""

Write-Host "Pods:"
kubectl get pods -n $Namespace

Write-Host ""
Write-Host "Deployments:"
kubectl get deployments -n $Namespace

Write-Host ""
Write-Host "Services:"
kubectl get services -n $Namespace