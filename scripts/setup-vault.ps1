param(
    [Parameter(Position = 0)]
    [ValidateSet("dev", "test", "prod")]
    [string]$Environment = "dev",

    # Vault root token — defaults to "root" which is the standard Vault dev-mode token
    [string]$VaultToken = "root",

    # Secret values — dev has sensible defaults; test/prod require explicit values
    [string]$MysqlDatabase,
    [string]$MysqlUser,
    [string]$MysqlPassword,
    [string]$MysqlRootPassword,
    [string]$JwtSecret,
    [string]$SecretKey
)

$ErrorActionPreference = "Stop"

. "$PSScriptRoot/common.ps1"

$Kubectl = Get-RequiredCommand "kubectl"

# ── Defaults (dev only) ──────────────────────────────────────────────────────
if ($Environment -eq "dev") {
    if (!$MysqlDatabase)     { $MysqlDatabase     = "comic_library_dev" }
    if (!$MysqlUser)         { $MysqlUser          = "comic_user_dev" }
    if (!$MysqlPassword)     { $MysqlPassword      = "dev_password" }
    if (!$MysqlRootPassword) { $MysqlRootPassword  = "dev_root_password" }
    if (!$JwtSecret)         { $JwtSecret          = "dev_jwt_secret" }
    if (!$SecretKey)         { $SecretKey          = "dev_secret_key" }
}
else {
    $missing = @()
    if (!$MysqlDatabase)     { $missing += "-MysqlDatabase" }
    if (!$MysqlUser)         { $missing += "-MysqlUser" }
    if (!$MysqlPassword)     { $missing += "-MysqlPassword" }
    if (!$MysqlRootPassword) { $missing += "-MysqlRootPassword" }
    if (!$JwtSecret)         { $missing += "-JwtSecret" }
    if (!$SecretKey)         { $missing += "-SecretKey" }
    if ($missing.Count -gt 0) {
        throw "The following parameters are required for the '$Environment' environment: $($missing -join ', ')"
    }
}

$Namespace = "comic-library-$Environment"

# ── Helper: run a vault command inside the vault-0 pod ──────────────────────
function Invoke-Vault {
    param([string[]]$VaultArgs)
    $result = & $Kubectl exec vault-0 `
        -- env "VAULT_TOKEN=$VaultToken" vault @VaultArgs 2>&1
    if ($LASTEXITCODE -ne 0) {
        # Surface the error as a string so callers can choose to swallow it
        throw ($result -join "`n")
    }
    return $result
}

# ── Helper: run a shell command inside vault-0 ──────────────────────────────
function Invoke-VaultShell {
    param([string]$ShellCommand)
    $result = & $Kubectl exec vault-0 `
        -- /bin/sh -c $ShellCommand 2>&1
    if ($LASTEXITCODE -ne 0) { throw ($result -join "`n") }
    return $result
}

Write-Host ""
Write-Host "==> Configuring Vault for environment: $Environment"
Write-Host ""

# ── 1. Enable Kubernetes auth (idempotent) ───────────────────────────────────
Write-Host "[1/5] Enabling Kubernetes auth method..."
try {
    Invoke-Vault @("auth", "enable", "kubernetes") | Out-Null
    Write-Host "      Enabled."
}
catch {
    if ($_ -match "already in use|path is already in use") {
        Write-Host "      Already enabled, skipping."
    }
    else { throw }
}

# ── 2. Configure Kubernetes auth ────────────────────────────────────────────
Write-Host "[2/5] Configuring Kubernetes auth (cluster connection)..."
Invoke-Vault @(
    "write", "auth/kubernetes/config",
    "kubernetes_host=https://kubernetes.default.svc",
    "token_reviewer_jwt=@/var/run/secrets/kubernetes.io/serviceaccount/token",
    "kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
) | Out-Null
Write-Host "      Done."

# ── 3. Write policy ──────────────────────────────────────────────────────────
Write-Host "[3/5] Writing Vault policy 'comic-book-library-policy'..."
$policyHCL = 'path "secret/data/comic-book-library/*" { capabilities = ["read"] }'
$policyB64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($policyHCL))
Invoke-VaultShell "echo '$policyB64' | base64 -d | VAULT_TOKEN=$VaultToken vault policy write comic-book-library-policy -" | Out-Null
Write-Host "      Done."

# ── 4. Create roles (one per service account per environment) ────────────────
Write-Host "[4/5] Creating Vault roles for $Environment..."

Invoke-Vault @(
    "write", "auth/kubernetes/role/comic-backend-$Environment",
    "bound_service_account_names=backend",
    "bound_service_account_namespaces=$Namespace",
    "policies=comic-book-library-policy",
    "ttl=24h"
) | Out-Null
Write-Host "      Role 'comic-backend-$Environment' created."

Invoke-Vault @(
    "write", "auth/kubernetes/role/comic-mysql-$Environment",
    "bound_service_account_names=mysql",
    "bound_service_account_namespaces=$Namespace",
    "policies=comic-book-library-policy",
    "ttl=24h"
) | Out-Null
Write-Host "      Role 'comic-mysql-$Environment' created."

# ── 5. Store secrets ─────────────────────────────────────────────────────────
Write-Host "[5/5] Enabling KV v2 secrets engine and storing secrets..."
try {
    Invoke-Vault @("secrets", "enable", "-path=secret", "kv-v2") | Out-Null
    Write-Host "      KV v2 engine enabled."
}
catch {
    if ($_ -match "already in use|path is already in use") {
        Write-Host "      KV v2 already enabled, skipping."
    }
    else { throw }
}

Invoke-Vault @(
    "kv", "put", "secret/comic-book-library/$Environment",
    "MYSQL_DATABASE=$MysqlDatabase",
    "MYSQL_USER=$MysqlUser",
    "MYSQL_PASSWORD=$MysqlPassword",
    "MYSQL_ROOT_PASSWORD=$MysqlRootPassword",
    "JWT_SECRET=$JwtSecret",
    "SECRET_KEY=$SecretKey"
) | Out-Null
Write-Host "      Secrets stored at: secret/comic-book-library/$Environment"

Write-Host ""
Write-Host "Vault setup complete for: $Environment"
Write-Host ""
Write-Host "You can now run:"
Write-Host "  .\scripts\deploy.ps1 $Environment"
Write-Host ""
