Write-Host "--- Starting Shift-Left Security Scan (Trivy-in-Docker) ---" -ForegroundColor Cyan

# 1. Scan Filesystem
Write-Host "Step 1: Scanning Filesystem for secrets and misconfigurations..." -ForegroundColor Yellow
# We mount the current directory ($PWD) to /root/ inside the container
docker run --rm -v ${PWD}:/root/ aquasec/trivy fs --exit-code 1 --severity HIGH,CRITICAL /root/

if ($LASTEXITCODE -ne 0) {
    Write-Error "BUILD RED: Critical vulnerabilities found in filesystem. Deployment halted."
    exit 1
}

# 2. Build and Scan Backend Image
Write-Host "`nStep 2: Building and Scanning Backend Image..." -ForegroundColor Yellow
docker build -t comic-backend:latest -f ./backend/Dockerfile .
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image --exit-code 1 --severity HIGH,CRITICAL comic-backend:latest

if ($LASTEXITCODE -ne 0) {
    Write-Error "BUILD RED: Critical vulnerabilities found in Backend Image. Deployment halted."
    exit 1
}

# 3. Build and Scan Frontend Image
Write-Host "`nStep 3: Building and Scanning Frontend Image..." -ForegroundColor Yellow
docker build -t comic-frontend:latest ./frontend
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image --exit-code 1 --severity HIGH,CRITICAL comic-frontend:latest

if ($LASTEXITCODE -ne 0) {
    Write-Error "BUILD RED: Critical vulnerabilities found in Frontend Image. Deployment halted."
    exit 1
}

Write-Host "`nBUILD GREEN: No high-severity vulnerabilities detected!" -ForegroundColor Green