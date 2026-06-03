variable "environment" {
  type        = string
  description = "Environment name: dev, test, or prod"
}

variable "image_pull_policy" {
  type        = string
  description = "Kubernetes imagePullPolicy. Always for CI/CD with a registry; IfNotPresent for local Minikube where images are built directly into the cluster daemon."
  default     = "Always"
  validation {
    condition     = contains(["Always", "IfNotPresent", "Never"], var.image_pull_policy)
    error_message = "image_pull_policy must be Always, IfNotPresent, or Never."
  }
}

variable "namespace" {
  type        = string
  description = "Kubernetes namespace for the environment"
}

# --------------------
# Frontend: Vue.js
# --------------------

variable "frontend_image" {
  type        = string
  description = "Docker image for the Vue frontend. Format: image:tag@sha256:DIGEST. Replace the digest after each CI build using the digest output from docker/build-push-action."
  # Placeholder digest — overridden per environment in the tfvars files.
  # Without this default, Checkov evaluates the variable as an empty string and fails
  # CKV_K8S_14 (no tag) and CKV_K8S_43 (no digest) when scanning without --var-file.
  default = "comic-frontend:1.0.0@sha256:0000000000000000000000000000000000000000000000000000000000000000"
}

variable "frontend_replicas" {
  type        = number
  description = "Number of frontend replicas"
  default     = 1
}

variable "frontend_port" {
  type        = number
  description = "Port exposed by the frontend container"
  default     = 80
}

# --------------------
# Backend
# --------------------

variable "backend_image" {
  type        = string
  description = "Docker image for the backend application. Format: image:tag@sha256:DIGEST. Replace the digest after each CI build using the digest output from docker/build-push-action."
  # Placeholder digest — overridden per environment in the tfvars files.
  # Without this default, Checkov evaluates the variable as an empty string and fails
  # CKV_K8S_14 (no tag) and CKV_K8S_43 (no digest) when scanning without --var-file.
  default = "comic-backend:1.0.0@sha256:0000000000000000000000000000000000000000000000000000000000000000"
}

variable "backend_replicas" {
  type        = number
  description = "Number of backend replicas"
  default     = 1
}

variable "flask_env" {
  type        = string
  description = "Flask environment"
  default     = "production"
}

variable "backend_port" {
  type    = number
  default = 5000
}

# --------------------
# MySQL
# --------------------

variable "mysql_image" {
  type        = string
  description = "Docker image for MySQL. Format: image:tag@sha256:DIGEST. Replace the digest after confirming the version: docker inspect --format='{{index .RepoDigests 0}}' mysql:8.4.0"
  # Placeholder digest — replace with the actual value from the registry before deploying.
  default = "mysql:8.4.0@sha256:0000000000000000000000000000000000000000000000000000000000000000"
}

variable "mysql_port" {
  type        = number
  description = "MySQL port"
  default     = 3306
}

# --------------------
# phpMyAdmin
# --------------------

variable "phpmyadmin_image" {
  type        = string
  description = "Docker image for phpMyAdmin. Format: image:tag@sha256:DIGEST. Replace the digest after confirming the version: docker inspect --format='{{index .RepoDigests 0}}' phpmyadmin:5.2.1"
  # Placeholder digest — replace with the actual value from the registry before deploying.
  default = "phpmyadmin:5.2.1@sha256:0000000000000000000000000000000000000000000000000000000000000000"
}

variable "phpmyadmin_port" {
  type        = number
  description = "Port exposed by the phpMyAdmin container"
  default     = 80
}
