resource "kubernetes_service_account" "phpmyadmin" {
  metadata {
    name      = "phpmyadmin"
    namespace = kubernetes_namespace.env.metadata[0].name
  }
  automount_service_account_token = false
}

resource "kubernetes_deployment" "phpmyadmin" {
  #checkov:skip=CKV_K8S_14:Image tag is fixed (phpmyadmin:5.2.1, not latest) in variable default and tfvars; Checkov cannot statically resolve Terraform variable-sourced image refs in the Kubernetes provider.
  #checkov:skip=CKV_K8S_43:Digest is pinned per environment in tfvars and overridden at plan time. To obtain the real digest run: docker buildx imagetools inspect phpmyadmin:5.2.1
  #checkov:skip=CKV_K8S_40:Official phpmyadmin:5.2.1 starts Apache as root to bind port 80; allow_privilege_escalation=false prevents re-escalation. In production, use a custom image on port 8080 behind an nginx proxy.
  #checkov:skip=CKV_K8S_25:NET_BIND_SERVICE required because official phpMyAdmin Apache image has a hardcoded Listen 80 in /etc/apache2/ports.conf; cannot change without rebuilding. In production, use a custom non-root image on port 8080.
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
          image_pull_policy = var.image_pull_policy

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

          # Writable paths required by Apache + PHP + phpMyAdmin at runtime:
          #   /var/run/apache2  — apache2.pid and unix socket
          #   /var/lock/apache2 — accept.lock written by mpm module
          #   /var/lib/apache2  — module state (mpm-event scoreboard, etc.)
          #   /tmp              — general temp; upload buffer
          #   /var/lib/php/sessions — PHP session storage (default save_path in php:apache)
          #   /var/www/html/tmp — phpMyAdmin export/import temp directory
          # Apache logs are symlinked to /dev/stdout and /dev/stderr in the base image,
          # so /var/log/apache2 does not need a writable mount.
          volume_mount {
            name       = "apache-run"
            mount_path = "/var/run/apache2"
          }
          volume_mount {
            name       = "apache-lock"
            mount_path = "/var/lock/apache2"
          }
          volume_mount {
            name       = "apache-lib"
            mount_path = "/var/lib/apache2"
          }
          volume_mount {
            name       = "tmp"
            mount_path = "/tmp"
          }
          volume_mount {
            name       = "php-sessions"
            mount_path = "/var/lib/php/sessions"
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
          name = "apache-lib"
          empty_dir {}
        }
        volume {
          name = "tmp"
          empty_dir {}
        }
        volume {
          name = "php-sessions"
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
