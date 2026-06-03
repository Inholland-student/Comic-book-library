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

        # run_as_user = 999 (mysql user) causes the entrypoint to skip the gosu privilege-drop
        # step, making allow_privilege_escalation=false and drop ALL safe without needing
        # SETUID/SETGID/CHOWN capabilities back.
        security_context {
          run_as_non_root = true
          run_as_user     = 999
          run_as_group    = 999
          fs_group        = 999
          seccomp_profile {
            type = "RuntimeDefault"
          }
        }

        container {
          name              = "mysql"
          image             = var.mysql_image
          image_pull_policy = var.image_pull_policy

          port {
            container_port = var.mysql_port
          }

          command = ["/bin/sh", "-c"]

          args = ["tr -d '\\r' < /vault/secrets/config > /tmp/vault-env && . /tmp/vault-env && exec docker-entrypoint.sh mysqld"]

          resources {
            requests = {
              cpu    = "250m"
              memory = "512Mi"
            }
            limits = {
              cpu    = "500m"
              memory = "1Gi"
            }
          }

          liveness_probe {
            exec {
              command = ["mysqladmin", "ping", "-h", "127.0.0.1"]
            }
            initial_delay_seconds = 30
            period_seconds        = 10
            timeout_seconds       = 5
            failure_threshold     = 3
          }

          readiness_probe {
            exec {
              command = ["mysqladmin", "ping", "-h", "127.0.0.1"]
            }
            initial_delay_seconds = 10
            period_seconds        = 5
            timeout_seconds       = 3
            failure_threshold     = 3
          }

          security_context {
            allow_privilege_escalation = false
            read_only_root_filesystem  = true
            capabilities {
              drop = ["ALL", "NET_RAW"]
            }
          }

          volume_mount {
            name       = "mysql-data"
            mount_path = "/var/lib/mysql"
          }
          volume_mount {
            name       = "mysql-run"
            mount_path = "/var/run/mysqld"
          }
          volume_mount {
            name       = "tmp"
            mount_path = "/tmp"
          }
        }

        volume {
          name = "mysql-data"
          empty_dir {}
        }
        volume {
          name = "mysql-run"
          empty_dir {}
        }
        volume {
          name = "tmp"
          empty_dir {}
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
