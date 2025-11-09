# Infrastructure as Code for User Service
terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

# Kubernetes namespace for user service
resource "kubernetes_namespace" "user_service" {
  metadata {
    name = "production"
  }
}

# Kubernetes deployment for user service
resource "kubernetes_deployment" "user_service" {
  metadata {
    name      = "user-service"
    namespace = kubernetes_namespace.user_service.metadata[0].name
    labels = {
      app = "user-service"
    }
  }

  spec {
    replicas = 2

    selector {
      match_labels = {
        app = "user-service"
      }
    }

    template {
      metadata {
        labels = {
          app = "user-service"
        }
      }

      spec {
        container {
          name  = "user-service"
          image = "registry.example.com/user-service:latest"

          port {
            container_port = 8080
          }

          env {
            name = "JWT_SECRET_KEY"
            value_from {
              secret_key_ref {
                name = "auth-secrets"
                key  = "JWT_SECRET_KEY"
              }
            }
          }

          resources {
            limits = {
              cpu    = "500m"
              memory = "512Mi"
            }
            requests = {
              cpu    = "250m"
              memory = "256Mi"
            }
          }
        }
      }
    }
  }
}

# Kubernetes service for user service
resource "kubernetes_service" "user_service" {
  metadata {
    name      = "user-service"
    namespace = kubernetes_namespace.user_service.metadata[0].name
  }

  spec {
    selector = {
      app = "user-service"
    }

    port {
      port        = 8080
      target_port = 8080
    }

    type = "ClusterIP"
  }
}