# Default deny all ingress for every pod in the namespace
resource "kubernetes_network_policy" "default_deny_ingress" {
  metadata {
    name      = "default-deny-ingress"
    namespace = kubernetes_namespace.env.metadata[0].name
  }
  spec {
    pod_selector {}
    policy_types = ["Ingress"]
  }
}

# Default deny all egress for every pod in the namespace
resource "kubernetes_network_policy" "default_deny_egress" {
  metadata {
    name      = "default-deny-egress"
    namespace = kubernetes_namespace.env.metadata[0].name
  }
  spec {
    pod_selector {}
    policy_types = ["Egress"]
  }
}

# Allow DNS egress for all pods (needed for service discovery)
resource "kubernetes_network_policy" "allow_dns_egress" {
  metadata {
    name      = "allow-dns-egress"
    namespace = kubernetes_namespace.env.metadata[0].name
  }
  spec {
    pod_selector {}
    policy_types = ["Egress"]
    egress {
      ports {
        port     = "53"
        protocol = "UDP"
      }
      ports {
        port     = "53"
        protocol = "TCP"
      }
    }
  }
}

# Frontend: allow ingress on the frontend port, egress only to backend
resource "kubernetes_network_policy" "frontend" {
  metadata {
    name      = "frontend-netpol"
    namespace = kubernetes_namespace.env.metadata[0].name
  }
  spec {
    pod_selector {
      match_labels = { app = "frontend" }
    }
    policy_types = ["Ingress", "Egress"]
    ingress {
      ports {
        port     = tostring(var.frontend_port)
        protocol = "TCP"
      }
    }
    egress {
      to {
        pod_selector {
          match_labels = { app = "backend" }
        }
      }
      ports {
        port     = tostring(var.backend_port)
        protocol = "TCP"
      }
    }
  }
}

# Backend: ingress from frontend only, egress to MySQL and Vault
resource "kubernetes_network_policy" "backend" {
  metadata {
    name      = "backend-netpol"
    namespace = kubernetes_namespace.env.metadata[0].name
  }
  spec {
    pod_selector {
      match_labels = { app = "backend" }
    }
    policy_types = ["Ingress", "Egress"]
    ingress {
      from {
        pod_selector {
          match_labels = { app = "frontend" }
        }
      }
      ports {
        port     = tostring(var.backend_port)
        protocol = "TCP"
      }
    }
    egress {
      to {
        pod_selector {
          match_labels = { app = "mysql" }
        }
      }
      ports {
        port     = tostring(var.mysql_port)
        protocol = "TCP"
      }
    }
    # Vault agent sidecar needs to reach the Vault server
    egress {
      ports {
        port     = "8200"
        protocol = "TCP"
      }
    }
  }
}

# MySQL: ingress from backend and phpMyAdmin only, egress to Vault
resource "kubernetes_network_policy" "mysql" {
  metadata {
    name      = "mysql-netpol"
    namespace = kubernetes_namespace.env.metadata[0].name
  }
  spec {
    pod_selector {
      match_labels = { app = "mysql" }
    }
    policy_types = ["Ingress", "Egress"]
    ingress {
      from {
        pod_selector {
          match_labels = { app = "backend" }
        }
      }
      ports {
        port     = tostring(var.mysql_port)
        protocol = "TCP"
      }
    }
    ingress {
      from {
        pod_selector {
          match_labels = { app = "phpmyadmin" }
        }
      }
      ports {
        port     = tostring(var.mysql_port)
        protocol = "TCP"
      }
    }
    # Vault agent sidecar needs to reach the Vault server
    egress {
      ports {
        port     = "8200"
        protocol = "TCP"
      }
    }
  }
}

# phpMyAdmin: allow ingress on the phpmyadmin port, egress only to MySQL
resource "kubernetes_network_policy" "phpmyadmin" {
  metadata {
    name      = "phpmyadmin-netpol"
    namespace = kubernetes_namespace.env.metadata[0].name
  }
  spec {
    pod_selector {
      match_labels = { app = "phpmyadmin" }
    }
    policy_types = ["Ingress", "Egress"]
    ingress {
      ports {
        port     = tostring(var.phpmyadmin_port)
        protocol = "TCP"
      }
    }
    egress {
      to {
        pod_selector {
          match_labels = { app = "mysql" }
        }
      }
      ports {
        port     = tostring(var.mysql_port)
        protocol = "TCP"
      }
    }
  }
}
