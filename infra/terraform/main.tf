locals {
  google_apis = toset([
    "run.googleapis.com",
    "secretmanager.googleapis.com",
  ])
  google_secrets = toset([
    "POSTGRESQL_USERNAME",
    "POSTGRESQL_PASSWORD",
    "POSTGRESQL_DATABASE",
    "POSTGRESQL_HOST",
    "POSTGRESQL_PORT",
  ])
}

resource "random_password" "supabase_password" {
  length      = 16
  special     = true
  min_lower   = 1
  min_upper   = 1
  min_numeric = 1
  min_special = 1
}

resource "supabase_project" "douglas_crawler" {
  organization_id   = var.supabase_organization_id
  name              = "douglas-crawler"
  database_password = random_password.supabase_password.result
  region            = var.supabase_region

  lifecycle {
    ignore_changes = [database_password, instance_size]
  }
}

resource "google_project_service" "default" {
  for_each = local.google_apis

  service            = each.value
  disable_on_destroy = true
}

resource "google_secret_manager_secret" "default" {
  for_each = local.google_secrets

  secret_id = each.value

  replication {
    auto {}
  }
}

resource "google_cloud_run_v2_service" "api" {
  name     = "douglas-crawler-api"
  location = var.gcp_region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    scaling {
      min_instance_count = 0
      max_instance_count = 1
    }

    containers {
      image = "docker.io/kvdomingo/douglas-crawler-api"

      dynamic "env" {
        for_each = google_secret_manager_secret.default

        content {
          name = env.key

          value_source {
            secret_key_ref {
              secret  = env.value.secret_id
              version = "latest"
            }
          }
        }
      }

      resources {
        cpu_idle          = true
        startup_cpu_boost = true

        limits = {
          cpu    = "100m"
          memory = "128Mi"
        }
      }

      ports {
        name           = "http1"
        container_port = 8000
      }

      startup_probe {
        initial_delay_seconds = 15
        timeout_seconds       = 5
        period_seconds        = 10
        failure_threshold     = 20

        http_get {
          path = "/api/health"
        }
      }

      liveness_probe {
        period_seconds    = 20
        timeout_seconds   = 5
        failure_threshold = 3

        http_get {
          path = "/api/health"
        }
      }
    }
  }
}
