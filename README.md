# Comic Book Library

A web app where users can browse and manage a comic book collection. Access is role-based — what you can see and do depends on your account type.

## User roles

| Role | What they can do |
|------|-----------------|
| Super admin | Can create admin accounts |
| Admin | Can add, edit, and delete comics; can create regular users |
| Friends | Can view the comic collection |
| Visitors (not logged in) | Cannot see anything |

---

## How to run the app

Make sure you have **Minikube** and **Docker** installed before starting.

**Step 1 — Start Minikube**
```powershell
minikube start
```

**Step 2 — Build the app images**
```powershell
minikube docker-env | Invoke-Expression
docker build -t comic-frontend:latest ./frontend
docker build -t comic-backend:latest ./backend
```

**Step 3 — Deploy everything**
```powershell
./scripts/deploy.ps1 dev
```

**Step 4 — Open the app** (wait until pods are running first)
```powershell
./scripts/open.ps1
```

To stop: `docker compose down`

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue.js 3 |
| Backend | Python (Flask) |
| Database | MySQL |
| DB management | phpMyAdmin (local only) |
| Infrastructure | Kubernetes via Minikube |

---

## Security practices

- **Secrets** (passwords, JWT keys, etc.) are stored in a `.env` file — never written directly in the code, never committed to Git
- **Passwords** are hashed with bcrypt before being stored
- **Login sessions** use JWT tokens in httpOnly cookies (safer than localStorage)
- **Forms** validate and sanitize all input to prevent SQL injection and XSS attacks
- **Role checks** happen on the server side, not just in the frontend UI
- `.env` is in `.gitignore` from the start

---

## How to start DefectDojo

DefectDojo is the dashboard where all security scan results are collected. The repo is already included in this project under the `defectdojo-repo` folder.

**Step 1 — Start DefectDojo**
```powershell
cd defectdojo-repo
docker compose up
```

**Step 2 — Wait for it to initialize**

This takes a few minutes the first time. Watch the logs — when you see `Admin password: ...` it's ready. Copy that password, you'll need it to log in.

**Step 3 — Open the dashboard**

Go to http://localhost:8080 and log in with:
- Username: `admin`
- Password: the one from the logs (ask a teammate if you missed it)

**Step 4 — To stop DefectDojo**
```powershell
docker compose down
```

---

## Security scanning (DefectDojo)

All security scan results are collected in **DefectDojo**, a vulnerability management dashboard.

**Access:** http://localhost:8080
**Login:** ask for .env

Findings are under: **Comic Book Library → Security Assessment 2026**

### Scans that have been run

| Tool | What it checks | Findings |
|------|---------------|---------|
| Checkov | Terraform / infrastructure misconfigurations | 4 Medium |
| Semgrep | Source code security issues (SAST) | 2 Medium |
| ZAP | Live app vulnerabilities (DAST) | 3 Low, 2 Info |
| Trivy | Known CVEs in dependencies and images (SCA) | 3 Medium, 1 Low |

### How to re-run the scans manually

Make sure the app is running before running ZAP. Run each command from the project root.

**Checkov** (checks Terraform config for misconfigurations)
```powershell
checkov -d terraform --output json > checkov-results.json

```

**Semgrep** (checks source code for security issues)
```powershell
semgrep scan --config auto --json --output semgrep-results.json backend/ frontend/
```

**Trivy** (checks dependencies for known vulnerabilities)
```powershell
docker run --rm -v "C:/meryamdouiri/cybersecurity/Comic book library:/src" aquasec/trivy:latest fs --format json --output /src/trivy-results.json --skip-dirs ".venv,backend/.venv,defectdojo-repo" --scanners vuln //src
```

**ZAP** (scans the live app for vulnerabilities — needs the app running first)
```powershell
docker run --rm -v "C:/meryamdouiri/cybersecurity/Comic book library:/zap/wrk" -t ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t http://host.docker.internal:8090 -x zap-results.xml -I
```

After running, upload the result files to DefectDojo via:
**Engagements → Security Assessment 2026 → Add Tests → Import Scan**
