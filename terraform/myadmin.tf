resource "kubernetes_service_account" "phpmyadmin" {
  metadata {
    name      = "phpmyadmin"
    namespace = kubernetes_namespace.env.metadata[0].name
  }
  automount_service_account_token = false
}

resource "kubernetes_deployment" "phpmyadmin" {
  # checkov:skip=CKV_K8S_40:The official phpmyadmin:5.2.1 image starts Apache as root to bind
  # port 80. Apache forks worker processes that run as www-data, but the master process must
  # start as root. With allow_privilege_escalation=false set below, no child process can
  # escalate back to root. In production, this is resolved by placing phpMyAdmin behind an
  # nginx reverse proxy on a non-privileged port and running the application as www-data.
  #
  # checkov:skip=CKV_K8S_25:NET_BIND_SERVICE is required because the official phpmyadmin:5.2.1
  # image configures Apache with a hardcoded Listen 80 directive in /etc/apache2/ports.conf.
  # Neither the phpMyAdmin Docker image nor the php:apache base image exposes an environment
  # variable that substitutes the listen port at runtime, making port reconfiguration impossible
  # without rebuilding the image. When ALL capabilities are dropped, NET_BIND_SERVICE must be
  # re-added for any process — including root — to bind a privileged port (< 1024).
  # In production: (a) build a custom image that listens on port 8080, or (b) deploy an nginx
  # sidecar as a reverse proxy that handles port 80 and forwards to phpMyAdmin on 8080, then
  # remove this capability entirely.
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
            read_only_root_filesystem  = true
            capabilities {
              drop = ["ALL", "NET_RAW"]
              # NET_BIND_SERVICE retained — see checkov:skip=CKV_K8S_25 above.
              add = ["NET_BIND_SERVICE"]
            }
          }

          # Apache writes its PID and lock files at startup; PHP uses /tmp for session storage
          # and upload temp files; phpMyAdmin uses /var/www/html/tmp for export temp files.
          # Apache logs in the official PHP Docker image are symlinked to /dev/stdout and
          # /dev/stderr, so /var/log/apache2 does not require a writable mount.
          volume_mount {
            name       = "apache-run"
            mount_path = "/var/run/apache2"
          }
          volume_mount {
            name       = "apache-lock"
            mount_path = "/var/lock/apache2"
          }
          volume_mount {
            name       = "tmp"
            mount_path = "/tmp"
          }
          volume_mount {
            name       = "pma-tmp"
            mount_path = "/var/www/html/tmp"
          }
        }

        volume {
          name = "apache-run"
          empty_dir {}
        }
        volume {
          name = "apache-lock"
          empty_dir {}
        }
        volume {
          name = "tmp"
          empty_dir {}
        }
        volume {
          name = "pma-tmp"
          empty_dir {}
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
