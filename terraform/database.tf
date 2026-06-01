resource "kubernetes_service_account" "mysql" {
  metadata {
    name      = "mysql"
    namespace = kubernetes_namespace.env.metadata[0].name
  }
}

resource "kubernetes_deployment" "mysql" {
  metadata {
    name      = "mysql"
    namespace = kubernetes_namespace.env.metadata[0].name

    labels = {
      app = "mysql"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "mysql"
      }
    }

    template {
      metadata {
        labels = {
          app = "mysql"
        }

        annotations = {
          "vault.hashicorp.com/agent-inject"                 = "true"
          "vault.hashicorp.com/role"                         = "comic-mysql-${var.environment}"
          "vault.hashicorp.com/agent-inject-secret-config"   = "secret/data/comic-book-library/${var.environment}"
          "vault.hashicorp.com/agent-inject-template-config" = <<EOT
{{- with secret "secret/data/comic-book-library/${var.environment}" -}}
export MYSQL_DATABASE="{{ .Data.data.MYSQL_DATABASE }}"
export MYSQL_USER="{{ .Data.data.MYSQL_USER }}"
export MYSQL_PASSWORD="{{ .Data.data.MYSQL_PASSWORD }}"
export MYSQL_ROOT_PASSWORD="{{ .Data.data.MYSQL_ROOT_PASSWORD }}"
{{- end }}
EOT
        }
      }

      spec {
        service_account_name = kubernetes_service_account.mysql.metadata[0].name

        container {
          name  = "mysql"
          image = var.mysql_image

          port {
            container_port = var.mysql_port
          }

          command = ["/bin/sh", "-c"]

          args = ["tr -d '\\r' < /vault/secrets/config > /tmp/vault-env && . /tmp/vault-env && exec docker-entrypoint.sh mysqld"]
        }
      }
    }
  }
}

resource "kubernetes_service" "mysql" {
  metadata {
    name      = "mysql-service"
    namespace = kubernetes_namespace.env.metadata[0].name
  }

  spec {
    selector = {
      app = "mysql"
    }

    port {
      port        = var.mysql_port
      target_port = var.mysql_port
    }

    type = "ClusterIP"
  }
}
