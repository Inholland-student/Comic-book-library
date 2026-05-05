variable "environment" {
  type        = string
  description = "Environment name: dev, test, or prod"
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
  description = "Docker image for the Vue frontend"
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
  description = "Docker image for the backend application"
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

variable "jwt_secret" {
  type        = string
  description = "JWT secret for backend"
  sensitive   = true
}

variable "secret_key" {
  type        = string
  description = "Flask secret key"
  sensitive   = true
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
  description = "Docker image for MySQL"
  default     = "mysql:8.4"
}

variable "mysql_port" {
  type        = number
  description = "MySQL port"
  default     = 3306
}

variable "mysql_database" {
  type        = string
  description = "MySQL database name"
}

variable "mysql_user" {
  type        = string
  description = "MySQL user"
}

variable "mysql_password" {
  type        = string
  description = "MySQL user password"
  sensitive   = true
}

variable "mysql_root_password" {
  type        = string
  description = "MySQL root password"
  sensitive   = true
}

# --------------------
# phpMyAdmin
# --------------------

variable "phpmyadmin_image" {
  type        = string
  description = "Docker image for phpMyAdmin"
  default     = "phpmyadmin:latest"
}

variable "phpmyadmin_port" {
  type        = number
  description = "Port exposed by the phpMyAdmin container"
  default     = 80
}