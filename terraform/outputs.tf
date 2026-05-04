output "environment" {
  description = "Current environment"
  value       = var.environment
}

output "namespace" {
  description = "Kubernetes namespace"
  value       = kubernetes_namespace.env.metadata[0].name
}

output "frontend_service_name" {
  description = "Frontend service name"
  value       = kubernetes_service.frontend.metadata[0].name
}

output "backend_service_name" {
  description = "Backend service name"
  value       = kubernetes_service.backend.metadata[0].name
}

output "mysql_service_name" {
  description = "MySQL service name"
  value       = kubernetes_service.mysql.metadata[0].name
}

output "phpmyadmin_service_name" {
  description = "phpMyAdmin service name"
  value       = kubernetes_service.phpmyadmin.metadata[0].name
}

output "mysql_internal_host" {
  description = "Internal MySQL hostname inside Kubernetes"
  value       = "${kubernetes_service.mysql.metadata[0].name}.${kubernetes_namespace.env.metadata[0].name}.svc.cluster.local"
}

output "backend_internal_url" {
  description = "Internal backend URL inside Kubernetes"
  value       = "http://${kubernetes_service.backend.metadata[0].name}:${var.backend_port}"
}

output "open_frontend_command" {
  description = "Command to open frontend in Minikube"
  value       = "minikube service ${kubernetes_service.frontend.metadata[0].name} -n ${kubernetes_namespace.env.metadata[0].name}"
}

output "open_phpmyadmin_command" {
  description = "Command to open phpMyAdmin in Minikube"
  value       = "minikube service ${kubernetes_service.phpmyadmin.metadata[0].name} -n ${kubernetes_namespace.env.metadata[0].name}"
}

output "check_pods_command" {
  description = "Command to check pods in this environment"
  value       = "kubectl get pods -n ${kubernetes_namespace.env.metadata[0].name}"
}

output "check_services_command" {
  description = "Command to check services in this environment"
  value       = "kubectl get services -n ${kubernetes_namespace.env.metadata[0].name}"
}