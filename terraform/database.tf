resource "kubernetes_secret" "mysql_secret" {
  metadata {
    name      = "mysql-secret"
    namespace = kubernetes_namespace.env.metadata[0].name
  }

  data = {
    MYSQL_DATABASE      = var.mysql_database
    MYSQL_USER          = var.mysql_user
    MYSQL_PASSWORD      = var.mysql_password
    MYSQL_ROOT_PASSWORD = var.mysql_root_password
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
      }

      spec {
        container {
          name  = "mysql"
          image = var.mysql_image

          port {
            container_port = var.mysql_port
          }

          env_from {
            secret_ref {
              name = kubernetes_secret.mysql_secret.metadata[0].name
            }
          }
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