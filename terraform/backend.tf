resource "kubernetes_service_account" "backend" {
  metadata {
    name      = "backend"
    namespace = kubernetes_namespace.env.metadata[0].name
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

        annotations = {
          "vault.hashicorp.com/agent-inject"                 = "true"
          "vault.hashicorp.com/role"                         = "comic-backend-${var.environment}"
          "vault.hashicorp.com/agent-inject-secret-config"   = "secret/data/comic-book-library/${var.environment}"
          "vault.hashicorp.com/agent-inject-template-config" = <<EOT
{{- with secret "secret/data/comic-book-library/${var.environment}" -}}
export DB_NAME="{{ .Data.data.MYSQL_DATABASE }}"
export DB_USER="{{ .Data.data.MYSQL_USER }}"
export DB_PASSWORD="{{ .Data.data.MYSQL_PASSWORD }}"
export JWT_SECRET="{{ .Data.data.JWT_SECRET }}"
export SECRET_KEY="{{ .Data.data.SECRET_KEY }}"
{{- end }}
EOT
        }
      }

      spec {
        service_account_name = kubernetes_service_account.backend.metadata[0].name

        container {
          name              = "backend"
          image             = var.backend_image
          image_pull_policy = "Never"

          port {
            container_port = var.backend_port
          }

          command = ["/bin/sh", "-c"]

          args = ["tr -d '\\r' < /vault/secrets/config > /tmp/vault-env && . /tmp/vault-env && exec ./entrypoint.sh python run.py"]

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
