variable "kubeconfig_path" {
  description = "Path to kubeconfig used by Terraform."
  type        = string
  default     = "~/.kube/config"
}

variable "namespace" {
  description = "Kubernetes namespace for the application."
  type        = string
}

variable "frontend_image" {
  description = "Frontend image name already built inside or loaded into Minikube."
  type        = string
  default     = "comic-frontend:latest"
}

variable "backend_image" {
  description = "Backend image name already built inside or loaded into Minikube."
  type        = string
  default     = "comic-backend:latest"
}

variable "frontend_replicas" {
  description = "Number of frontend pods."
  type        = number
  default     = 1
}

variable "backend_replicas" {
  description = "Number of backend pods."
  type        = number
  default     = 1
}

variable "frontend_service_type" {
  description = "Frontend service type for Minikube access."
  type        = string
  default     = "NodePort"
}

variable "flask_env" {
  description = "Flask environment for the backend container."
  type        = string
  default     = "development"
}

variable "db_host" {
  description = "Database host reachable from the Kubernetes cluster."
  type        = string
  default     = "mysql"
}

variable "db_port" {
  description = "Database port."
  type        = number
  default     = 3306
}

variable "db_user" {
  description = "Database username."
  type        = string
  default     = "comic_user"
}

variable "db_password" {
  description = "Database password."
  type        = string
  sensitive   = true
  default     = "change-me"
}

variable "db_name" {
  description = "Database name."
  type        = string
  default     = "comic_library"
}

variable "mysql_image" {
  description = "MySQL image used for the in-cluster database."
  type        = string
  default     = "mysql:8.0"
}

variable "mysql_storage_size" {
  description = "Persistent volume size for MySQL."
  type        = string
  default     = "2Gi"
}

variable "mysql_root_password" {
  description = "MySQL root password."
  type        = string
  sensitive   = true
  default     = "change-me-root-password"
}

variable "jwt_secret" {
  description = "JWT signing secret."
  type        = string
  sensitive   = true
  default     = "change-me-super-secret-jwt-key"
}

variable "secret_key" {
  description = "Flask secret key."
  type        = string
  sensitive   = true
  default     = "change-me-flask-secret-key"
}

variable "import_created_by" {
  description = "Value passed to the backend import script."
  type        = string
  default     = ""
}
