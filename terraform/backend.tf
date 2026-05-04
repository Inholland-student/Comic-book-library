resource "kubernetes_secret" "backend_secret" {
  metadata {
    name      = "backend-secret"
    namespace = kubernetes_namespace.env.metadata[0].name
  }

  data = {
    JWT_SECRET = var.jwt_secret
    SECRET_KEY = var.secret_key
  }
}

resource "kubernetes_deployment" "backend" {
  metadata {
    name      = "backend"
    namespace = kubernetes_namespace.env.metadata[0].name

    labels = {
      app = "backend"
    }
  }

  spec {
    replicas = var.backend_replicas

    selector {
      match_labels = {
        app = "backend"
      }
    }

    template {
      metadata {
        labels = {
          app = "backend"
        }
      }

      spec {
        container {
          name              = "backend"
          image             = var.backend_image
          image_pull_policy = "Never"

          port {
            container_port = var.backend_port
          }

          env {
            name  = "APP_ENV"
            value = var.environment
          }

          env {
            name  = "FLASK_ENV"
            value = var.flask_env
          }

          env {
            name  = "DB_HOST"
            value = kubernetes_service.mysql.metadata[0].name
          }

          env {
            name  = "DB_PORT"
            value = tostring(var.mysql_port)
          }

          env {
            name  = "DB_NAME"
            value = var.mysql_database
          }

          env {
            name  = "DB_USER"
            value = var.mysql_user
          }

          env {
            name = "DB_PASSWORD"

            value_from {
              secret_key_ref {
                name = kubernetes_secret.mysql_secret.metadata[0].name
                key  = "MYSQL_PASSWORD"
              }
            }
          }

          env {
            name = "JWT_SECRET"

            value_from {
              secret_key_ref {
                name = kubernetes_secret.backend_secret.metadata[0].name
                key  = "JWT_SECRET"
              }
            }
          }

          env {
            name = "SECRET_KEY"

            value_from {
              secret_key_ref {
                name = kubernetes_secret.backend_secret.metadata[0].name
                key  = "SECRET_KEY"
              }
            }
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "backend" {
  metadata {
    name      = "backend-service"
    namespace = kubernetes_namespace.env.metadata[0].name
  }

  spec {
    selector = {
      app = "backend"
    }

    port {
      port        = var.backend_port
      target_port = var.backend_port
    }

    type = "ClusterIP"
  }
}