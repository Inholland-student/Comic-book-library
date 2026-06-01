Write-Host "--- Starting Shift-Left Security Scan (Trivy-in-Docker) ---" -ForegroundColor Cyan

Write-Host "Step 1: Scanning filesystem..." -ForegroundColor Yellow
docker run --rm -v ${PWD}:/root/ aquasec/trivy fs `
    --exit-code 1 `
    --severity HIGH,CRITICAL `
    --ignore-unfixed `
    --scanners vuln `
    --timeout 30m `
    --ignorefile /root/.trivyignore `
    /root/

if ($LASTEXITCODE -ne 0) {
    Write-Error "BUILD RED: Critical vulnerabilities found in filesystem. Deployment halted."
    exit 1
}

Write-Host "`nStep 2: Building and scanning backend image..." -ForegroundColor Yellow
docker build --no-cache -t comic-backend:latest ./backend
docker run --rm `
    -v /var/run/docker.sock:/var/run/docker.sock `
    -v ${PWD}/.trivyignore:/tmp/.trivyignore:ro `
    aquasec/trivy image `
    --scanners vuln `
    --ignore-unfixed `
    --ignorefile /tmp/.trivyignore `
    --exit-code 1 `
    --severity HIGH,CRITICAL `
    comic-backend:latest

if ($LASTEXITCODE -ne 0) {
    Write-Error "BUILD RED: Critical vulnerabilities found in backend image. Deployment halted."
    exit 1
}

Write-Host "`nStep 3: Building and scanning frontend image..." -ForegroundColor Yellow
docker build --no-cache -t comic-frontend:latest ./frontend
docker run --rm `
    -v /var/run/docker.sock:/var/run/docker.sock `
    -v ${PWD}/.trivyignore:/tmp/.trivyignore:ro `
    aquasec/trivy image `
    --scanners vuln `
    --ignore-unfixed `
    --ignorefile /tmp/.trivyignore `
    --exit-code 1 `
    --severity HIGH,CRITICAL `
    comic-frontend:latest

if ($LASTEXITCODE -ne 0) {
    Write-Error "BUILD RED: Critical vulnerabilities found in frontend image. Deployment halted."
    exit 1
}

Write-Host "`nBUILD GREEN: No high-severity vulnerabilities detected!" -ForegroundColor Green
