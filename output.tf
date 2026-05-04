output "namespace" {
  value = kubernetes_namespace.comic_ns.metadata[0].name
}

output "frontend_service_name" {
  value = kubernetes_service.frontend.metadata[0].name
}

output "backend_service_name" {
  value = kubernetes_service.backend.metadata[0].name
}

output "mysql_service_name" {
  value = kubernetes_service.mysql.metadata[0].name
}

output "frontend_access_command" {
  value = "minikube service ${kubernetes_service.frontend.metadata[0].name} -n ${kubernetes_namespace.comic_ns.metadata[0].name}"
}
