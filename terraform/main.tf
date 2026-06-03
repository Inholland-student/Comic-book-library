terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.35"
    }
  }
}

provider "kubernetes" {
  config_path = "~/.kube/config"
}

resource "kubernetes_namespace" "env" {
  metadata {
    name = var.namespace

    labels = {
      environment = var.environment
      project     = "comic-book-library"
    }
  }
}