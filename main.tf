terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.25"
    }
  }
}

provider "kubernetes" {
  config_path = var.kubeconfig_path
}

resource "kubernetes_namespace" "comic_ns" {
  metadata {
    name = var.namespace
  }
}

resource "kubernetes_secret" "mysql_auth" {
  metadata {
    name      = "mysql-auth"
    namespace = kubernetes_namespace.comic_ns.metadata[0].name
  }

  data = {
    MYSQL_ROOT_PASSWORD = var.mysql_root_password
    MYSQL_DATABASE      = var.db_name
    MYSQL_USER          = var.db_user
    MYSQL_PASSWORD      = var.db_password
  }

  type = "Opaque"
}

resource "kubernetes_config_map" "mysql_init" {
  metadata {
    name      = "mysql-init-sql"
    namespace = kubernetes_namespace.comic_ns.metadata[0].name
  }

  data = {
    "init.sql" = <<-SQL
      CREATE TABLE IF NOT EXISTS users (
        id INT NOT NULL AUTO_INCREMENT,
        username VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        role ENUM('super_admin','admin','friend') NOT NULL DEFAULT 'friend',
        created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        uuid CHAR(36) NOT NULL DEFAULT (UUID()),
        PRIMARY KEY (id),
        UNIQUE KEY username (username),
        UNIQUE KEY email (email),
        UNIQUE KEY uq_users_uuid (uuid),
        KEY idx_username (username),
        KEY idx_role (role)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

      CREATE TABLE IF NOT EXISTS comics (
        id INT NOT NULL AUTO_INCREMENT,
        serie VARCHAR(255) NOT NULL,
        number VARCHAR(50) NOT NULL,
        title VARCHAR(255) NOT NULL,
        created_by INT NOT NULL,
        created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (id),
        KEY idx_serie (serie),
        KEY idx_created_by (created_by),
        CONSTRAINT comics_ibfk_1 FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE CASCADE
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

      INSERT IGNORE INTO users (id, username, email, password_hash, role, uuid)
      VALUES
        (1, 'super_admin', 'super_admin@test.local', '$2b$12$cCe2YAw1SUxpzaxk7jLdruGh4TgulgmussGwpQZzZWz3WNVvJFrNe', 'super_admin', 'e2869bc8-3901-11f1-847b-2a56120d12fc'),
        (2, 'admin', 'admin@gmail.com', '$2b$12$cCe2YAw1SUxpzaxk7jLdruGh4TgulgmussGwpQZzZWz3WNVvJFrNe', 'admin', 'e286aa3c-3901-11f1-847b-2a56120d12fc');

      INSERT IGNORE INTO comics (id, serie, number, title, created_by)
      VALUES
        (1, 'Tom & Jerry (De Vrijbuiter)', 'A064', 'De Muizenvanger', 1),
        (2, 'Thomas Pips', 'C03', 'De Spekschieters', 1),
        (3, 'Robbedoes Weekblad', '1991', '2752', 1),
        (4, 'Eppo', '1980', '35', 1),
        (5, 'Fanfarax', '0', 'In Marseille (Taptoe)', 1);
    SQL
  }
}

resource "kubernetes_persistent_volume_claim" "mysql_data" {
  metadata {
    name      = "mysql-data"
    namespace = kubernetes_namespace.comic_ns.metadata[0].name
  }

  spec {
    access_modes = ["ReadWriteOnce"]

    resources {
      requests = {
        storage = var.mysql_storage_size
      }
    }
  }
}

resource "kubernetes_deployment" "mysql" {
  metadata {
    name      = "mysql"
    namespace = kubernetes_namespace.comic_ns.metadata[0].name
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
            container_port = 3306
          }

          env {
            name = "MYSQL_ROOT_PASSWORD"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.mysql_auth.metadata[0].name
                key  = "MYSQL_ROOT_PASSWORD"
              }
            }
          }

          env {
            name = "MYSQL_DATABASE"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.mysql_auth.metadata[0].name
                key  = "MYSQL_DATABASE"
              }
            }
          }

          env {
            name = "MYSQL_USER"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.mysql_auth.metadata[0].name
                key  = "MYSQL_USER"
              }
            }
          }

          env {
            name = "MYSQL_PASSWORD"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.mysql_auth.metadata[0].name
                key  = "MYSQL_PASSWORD"
              }
            }
          }

          volume_mount {
            name       = "mysql-data"
            mount_path = "/var/lib/mysql"
          }

          volume_mount {
            name       = "mysql-init"
            mount_path = "/docker-entrypoint-initdb.d/init.sql"
            sub_path   = "init.sql"
          }

          readiness_probe {
            tcp_socket {
              port = 3306
            }

            initial_delay_seconds = 15
            period_seconds        = 5
          }

          liveness_probe {
            tcp_socket {
              port = 3306
            }

            initial_delay_seconds = 30
            period_seconds        = 10
          }
        }

        volume {
          name = "mysql-data"

          persistent_volume_claim {
            claim_name = kubernetes_persistent_volume_claim.mysql_data.metadata[0].name
          }
        }

        volume {
          name = "mysql-init"

          config_map {
            name = kubernetes_config_map.mysql_init.metadata[0].name
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "mysql" {
  metadata {
    name      = "mysql"
    namespace = kubernetes_namespace.comic_ns.metadata[0].name
  }

  spec {
    selector = {
      app = kubernetes_deployment.mysql.spec[0].template[0].metadata[0].labels.app
    }

    port {
      port        = 3306
      target_port = 3306
    }

    type = "ClusterIP"
  }
}

resource "kubernetes_secret" "backend_env" {
  metadata {
    name      = "backend-env"
    namespace = kubernetes_namespace.comic_ns.metadata[0].name
  }

  data = {
    DB_HOST     = var.db_host
    DB_PORT     = tostring(var.db_port)
    DB_USER     = var.db_user
    DB_PASSWORD = var.db_password
    DB_NAME     = var.db_name
    JWT_SECRET  = var.jwt_secret
    SECRET_KEY  = var.secret_key
  }

  type = "Opaque"
}

resource "kubernetes_deployment" "backend" {
  metadata {
    name      = "backend"
    namespace = kubernetes_namespace.comic_ns.metadata[0].name
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
            container_port = 5000
          }

          env {
            name  = "FLASK_ENV"
            value = var.flask_env
          }

          env {
            name = "DB_HOST"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.backend_env.metadata[0].name
                key  = "DB_HOST"
              }
            }
          }

          env {
            name = "DB_PORT"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.backend_env.metadata[0].name
                key  = "DB_PORT"
              }
            }
          }

          env {
            name = "DB_USER"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.backend_env.metadata[0].name
                key  = "DB_USER"
              }
            }
          }

          env {
            name = "DB_PASSWORD"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.backend_env.metadata[0].name
                key  = "DB_PASSWORD"
              }
            }
          }

          env {
            name = "DB_NAME"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.backend_env.metadata[0].name
                key  = "DB_NAME"
              }
            }
          }

          env {
            name = "JWT_SECRET"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.backend_env.metadata[0].name
                key  = "JWT_SECRET"
              }
            }
          }

          env {
            name = "SECRET_KEY"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.backend_env.metadata[0].name
                key  = "SECRET_KEY"
              }
            }
          }

          liveness_probe {
            http_get {
              path = "/health"
              port = 5000
            }

            initial_delay_seconds = 20
            period_seconds        = 10
          }

          readiness_probe {
            http_get {
              path = "/health"
              port = 5000
            }

            initial_delay_seconds = 10
            period_seconds        = 5
          }
        }

      }
    }
  }

  depends_on = [kubernetes_service.mysql]
}

resource "kubernetes_service" "backend" {
  metadata {
    name      = "backend-service"
    namespace = kubernetes_namespace.comic_ns.metadata[0].name
  }

  spec {
    selector = {
      app = kubernetes_deployment.backend.spec[0].template[0].metadata[0].labels.app
    }

    port {
      port        = 5000
      target_port = 5000
    }

    type = "ClusterIP"
  }
}

resource "kubernetes_deployment" "frontend" {
  metadata {
    name      = "frontend"
    namespace = kubernetes_namespace.comic_ns.metadata[0].name
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
        container {
          name              = "frontend"
          image             = var.frontend_image
          image_pull_policy = "Never"

          port {
            container_port = 80
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "frontend" {
  metadata {
    name      = "frontend-service"
    namespace = kubernetes_namespace.comic_ns.metadata[0].name
  }

  spec {
    selector = {
      app = kubernetes_deployment.frontend.spec[0].template[0].metadata[0].labels.app
    }

    port {
      port        = 80
      target_port = 80
    }

    type = var.frontend_service_type
  }
}
