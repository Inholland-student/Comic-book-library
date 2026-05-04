resource "kubernetes_deployment" "frontend" {
  metadata {
    name      = "frontend"
    namespace = kubernetes_namespace.env.metadata[0].name

    labels = {
      app = "frontend"
    }
  }

  spec {
    replicas = var.frontend_replicas

    selector {
      match_labels = {
        app = "frontend"
      }
    }

    template {
      metadata {
        labels = {
          app = "frontend"
        }
      }

      spec {
        container {
          name              = "frontend"
          image             = var.frontend_image
          image_pull_policy = "Never"

          port {
            container_port = var.frontend_port
          }

          env {
            name  = "APP_ENV"
            value = var.environment
          }

          env {
            name  = "BACKEND_URL"
            value = "http://${kubernetes_service.backend.metadata[0].name}:${var.backend_port}"
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "frontend" {
  metadata {
    name      = "frontend-service"
    namespace = kubernetes_namespace.env.metadata[0].name
  }

  spec {
    selector = {
      app = "frontend"
    }

    port {
      port        = 80
      target_port = var.frontend_port
    }

    type = "NodePort"
  }
}