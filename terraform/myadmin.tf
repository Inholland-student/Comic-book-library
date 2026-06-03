resource "kubernetes_service_account" "phpmyadmin" {
  metadata {
    name      = "phpmyadmin"
    namespace = kubernetes_namespace.env.metadata[0].name
  }
  automount_service_account_token = false
}

resource "kubernetes_deployment" "phpmyadmin" {
  # checkov:skip=CKV_K8S_40:phpMyAdmin's official image starts Apache as root to bind port 80
  # (< 1024). CAP_NET_BIND_SERVICE is kept below. In production, place phpMyAdmin behind an
  # nginx reverse proxy on port 8080 and run the app as www-data.
  # checkov:skip=CKV_K8S_22:The official phpMyAdmin image writes session data, Apache PID/lock
  # files, and upload temp files across /var/run/apache2, /var/lock/apache2,
  # /var/lib/php/sessions, and /var/www/html/tmp. These paths are not documented in the image
  # spec and mapping them safely requires image-specific testing outside the scope of this
  # assignment. In production, use a custom image with explicit writable paths.
  metadata {
    name      = "phpmyadmin"
    namespace = kubernetes_namespace.env.metadata[0].name

    labels = {
      app = "phpmyadmin"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "phpmyadmin"
      }
    }

    template {
      metadata {
        labels = {
          app = "phpmyadmin"
        }
      }

      spec {
        service_account_name            = kubernetes_service_account.phpmyadmin.metadata[0].name
        automount_service_account_token = false

        security_context {
          seccomp_profile {
            type = "RuntimeDefault"
          }
        }

        container {
          name              = "phpmyadmin"
          image             = var.phpmyadmin_image
          image_pull_policy = "Always"

          port {
            container_port = var.phpmyadmin_port
          }

          env {
            name  = "PMA_HOST"
            value = kubernetes_service.mysql.metadata[0].name
          }

          env {
            name  = "PMA_PORT"
            value = tostring(var.mysql_port)
          }

          resources {
            requests = {
              cpu    = "50m"
              memory = "128Mi"
            }
            limits = {
              cpu    = "200m"
              memory = "256Mi"
            }
          }

          liveness_probe {
            http_get {
              path = "/"
              port = var.phpmyadmin_port
            }
            initial_delay_seconds = 15
            period_seconds        = 20
            timeout_seconds       = 5
            failure_threshold     = 3
          }

          readiness_probe {
            http_get {
              path = "/"
              port = var.phpmyadmin_port
            }
            initial_delay_seconds = 10
            period_seconds        = 10
            timeout_seconds       = 3
            failure_threshold     = 3
          }

          security_context {
            allow_privilege_escalation = false
            read_only_root_filesystem  = false
            capabilities {
              drop = ["ALL", "NET_RAW"]
              # NET_BIND_SERVICE is required: Apache binds port 80 (< 1024).
              # Dropping ALL removes this even for the root process.
              add = ["NET_BIND_SERVICE"]
            }
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "phpmyadmin" {
  metadata {
    name      = "phpmyadmin-service"
    namespace = kubernetes_namespace.env.metadata[0].name
  }

  spec {
    selector = {
      app = "phpmyadmin"
    }

    port {
      port        = 80
      target_port = var.phpmyadmin_port
    }

    type = "NodePort"
  }
}
