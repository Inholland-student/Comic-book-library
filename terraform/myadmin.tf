resource "kubernetes_deployment" "phpmyadmin" {
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
        container {
          name  = "phpmyadmin"
          image = var.phpmyadmin_image

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