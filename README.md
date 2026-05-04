# Comic Book Library

Create a web application to display a comic book library.

## Stack

- Frontend: Vue 3
- Backend: Flask
- Database: MySQL
- Local container workflow: Docker / Minikube / Kubernetes / Terraform

## Run With Docker Compose

```powershell
docker compose down -v
docker compose up --build
```

## Run With Minikube + Terraform

### 1. Start Minikube

```powershell
minikube start --driver=docker
kubectl get nodes
```

### 2. Build Docker images

Option A: build directly into Minikube's Docker daemon

```powershell
minikube image build -t comic-backend:latest .\backend
minikube image build -t comic-frontend:latest .\frontend
```

Option B: build with local Docker, then load into Minikube

```powershell
docker build -t comic-backend:latest .\backend
docker build -t comic-frontend:latest .\frontend
minikube image load comic-backend:latest
minikube image load comic-frontend:latest
```

### 3. Apply Terraform

Create a local secrets file that is not committed to Git, for example `secret.dev.tfvars`:

```hcl
db_password         = "replace-me"
mysql_root_password = "replace-me"
jwt_secret          = "replace-me-with-a-long-random-secret"
secret_key          = "replace-me-with-another-long-random-secret"
```

The Terraform config deploys:

- `mysql` deployment + `mysql` service (`ClusterIP`)
- `backend` deployment + `backend-service` (`ClusterIP`)
- `frontend` deployment + `frontend-service` (`NodePort`)

The frontend container serves the built Vue app through Nginx and proxies `/api` requests to `backend-service`, so the browser only needs the frontend service URL.

```powershell
terraform init
terraform fmt
terraform apply -var-file="envs/dev.tfvars" -var-file="secret.dev.tfvars"
```

### 4. Check resources

```powershell
kubectl get pods -n comic-dev
kubectl get svc -n comic-dev
```

### 5. Open the frontend

```powershell
minikube service frontend-service -n comic-dev
```

## Reset MySQL Data

If you change the MySQL seed schema or want to reinitialize the database from scratch, delete the MySQL workload and its persistent volume claim, then re-apply Terraform:

```powershell
kubectl delete deployment mysql -n comic-dev
kubectl delete pvc mysql-data -n comic-dev
terraform apply -var-file="envs/dev.tfvars" -var-file="secret.dev.tfvars"
```

## Terraform Notes

- Terraform uses the Kubernetes provider and creates native Kubernetes resources directly from `main.tf`.
- MySQL uses the official `mysql:8.0` image and is initialized with a compact schema, seed users, and a few sample comics from Terraform.
- MySQL data is stored in a simple PersistentVolumeClaim, which works well with Minikube's default storage class.
- The full dataset files are too large for a Kubernetes ConfigMap, so this Minikube setup seeds a small sample dataset instead of importing the entire CSV automatically.
- The backend image uses `imagePullPolicy = "Never"` so Minikube uses the image you built or loaded locally.
- Backend environment variables are stored in a Kubernetes secret created by Terraform.
- Real secret values should live in a local ignored `secret.dev.tfvars` file or in `TF_VAR_...` environment variables, not in Git-tracked Terraform files.
- Terraform `sensitive = true` only hides values from CLI output; the real values can still appear in Terraform state.
- The backend now connects to the in-cluster MySQL service at `DB_HOST=mysql` by default.

## Important Variables

Use `envs/*.tfvars` for non-secret environment settings and keep secrets in a local ignored file or `TF_VAR_...` environment variables:

- `frontend_image`
- `backend_image`
- `frontend_replicas`
- `backend_replicas`
- `db_host`
- `db_port`
- `db_user`
- `db_password`
- `db_name`
- `mysql_image`
- `mysql_storage_size`
- `mysql_root_password`
- `jwt_secret`
- `secret_key`

## Current Security / Project Notes

- Secrets should stay out of Git and out of hardcoded source files.
- Passwords are hashed with bcrypt.
- Authentication uses JWT in httpOnly cookies.
- RBAC is enforced server-side.

## Safer Secret Options

Option 1: local ignored tfvars file

```powershell
terraform apply -var-file="envs/dev.tfvars" -var-file="secret.dev.tfvars"
```

Option 2: environment variables

```powershell
$env:TF_VAR_db_password="replace-me"
$env:TF_VAR_mysql_root_password="replace-me"
$env:TF_VAR_jwt_secret="replace-me-with-a-long-random-secret"
$env:TF_VAR_secret_key="replace-me-with-another-long-random-secret"
terraform apply -var-file="envs/dev.tfvars"
```

## Stop Local Compose Stack

```powershell
docker compose down
```

