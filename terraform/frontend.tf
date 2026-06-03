resource "kubernetes_service_account" "frontend" {
  metadata {
    name      = "frontend"
    namespace = kubernetes_namespace.env.metadata[0].name
  }
  automount_service_account_token = false
}

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
        service_account_name            = kubernetes_service_account.frontend.metadata[0].name
        automount_service_account_token = false

        security_context {
          run_as_non_root = true
          run_as_user     = 101
          run_as_group    = 101
          fs_group        = 101
          seccomp_profile {
            type = "RuntimeDefault"
          }
        }

        container {
          name              = "frontend"
          image             = var.frontend_image
          image_pull_policy = "Always"

          port {
            container_port = var.frontend_port
          }

          env {
            name  = "APP_ENV"
            value = var.environment
          }

          env {
            name  = "BACKEND_PROXY_TARGET"
            value = "http://${kubernetes_service.backend.metadata[0].name}:${var.backend_port}"
          }

          resources {
            requests = {
              cpu    = "100m"
              memory = "128Mi"
            }
            limits = {
              cpu    = "250m"
              memory = "256Mi"
            }
          }

          liveness_probe {
            http_get {
              path = "/"
              port = var.frontend_port
            }
            initial_delay_seconds = 10
            period_seconds        = 15
            timeout_seconds       = 5
            failure_threshold     = 3
          }

          readiness_probe {
            http_get {
              path = "/"
              port = var.frontend_port
            }
            initial_delay_seconds = 5
            period_seconds        = 10
            timeout_seconds       = 3
            failure_threshold     = 3
          }

          security_context {
            allow_privilege_escalation = false
            read_only_root_filesystem  = true
            run_as_non_root            = true
            run_as_user                = 101
            capabilities {
              drop = ["ALL", "NET_RAW"]
            }
          }

          # nginx needs to write cache, the processed template output, its PID file, and tmp
          volume_mount {
            name       = "nginx-cache"
            mount_path = "/var/cache/nginx"
          }
          volume_mount {
            name       = "nginx-conf"
            mount_path = "/etc/nginx/conf.d"
          }
          volume_mount {
            name       = "nginx-run"
            mount_path = "/var/run"
          }
          volume_mount {
            name       = "tmp"
            mount_path = "/tmp"
          }
        }

        volume {
          name = "nginx-cache"
          empty_dir {}
        }
        volume {
          name = "nginx-conf"
          empty_dir {}
        }
        volume {
          name = "nginx-run"
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
