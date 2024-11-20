locals {
  google_apis = toset([
    "cloudresourcemanager.googleapis.com",
    "compute.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
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
  compute_engine_sa_roles = toset([
    "roles/run.invoker",
    "roles/secretmanager.secretAccessor",
    "roles/secretmanager.viewer",
  ])
  gha_sa_roles = toset([
    "roles/editor",
  ])
  run_image = "docker.io/kvdomingo/douglas-crawler-api"
}

data "google_project" "project" {}

data "google_compute_default_service_account" "default" {
  depends_on = [google_project_service.default["compute.googleapis.com"]]
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

resource "google_service_account" "github_actions_sa" {
  account_id  = "github-actions-sa"
  description = "GitHub Actions Service Account"
}

resource "google_service_account_iam_member" "github_actions_sa_wif_member" {
  member             = "principalSet://iam.googleapis.com/projects/${data.google_project.project.number}/locations/global/workloadIdentityPools/${google_iam_workload_identity_pool.github_actions_pool.workload_identity_pool_id}/attribute.repository/${var.github_repo_id}"
  role               = "roles/iam.serviceAccountTokenCreator"
  service_account_id = google_service_account.github_actions_sa.id
}

resource "google_project_iam_member" "github_actions_secret_accessor" {
  member  = "serviceAccount:${google_service_account.github_actions_sa.email}"
  project = data.google_project.project.project_id
  role    = "roles/secretmanager.secretAccessor"
}

resource "google_project_iam_member" "github_actions_sa" {
  for_each = local.gha_sa_roles

  member  = "serviceAccount:${google_service_account.github_actions_sa.email}"
  project = data.google_project.project.project_id
  role    = each.value
}

resource "google_project_iam_member" "compute_engine_sa" {
  for_each = local.compute_engine_sa_roles

  member  = "serviceAccount:${data.google_compute_default_service_account.default.email}"
  project = data.google_project.project.project_id
  role    = each.value
}

resource "google_iam_workload_identity_pool" "github_actions_pool" {
  workload_identity_pool_id = "github-pool"
  display_name              = "GitHub Actions Pool"
}

resource "google_iam_workload_identity_pool_provider" "github_provider" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github_actions_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-pool-provider"
  display_name                       = "GitHub Actions Provider"

  attribute_mapping = {
    "google.subject"             = "assertion.sub"
    "attribute.repository"       = "assertion.repository_id"
    "attribute.repository_owner" = "assertion.repository_owner_id"
  }

  attribute_condition = "attribute.repository == \"${var.github_repo_id}\""

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

resource "google_cloud_run_v2_service" "api" {
  depends_on = [google_project_iam_member.compute_engine_sa]

  name                = "douglas-crawler-api"
  location            = var.gcp_region
  ingress             = "INGRESS_TRAFFIC_ALL"
  deletion_protection = false

  template {
    max_instance_request_concurrency = 80
    timeout                          = "60s"

    scaling {
      min_instance_count = 0
      max_instance_count = 1
    }

    containers {
      image = local.run_image

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
          cpu    = "1"
          memory = "256Mi"
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
        timeout_seconds   = 3
        failure_threshold = 3

        http_get {
          path = "/api/health"
        }
      }
    }
  }
}

resource "google_cloud_run_service_iam_binding" "default" {
  service = google_cloud_run_v2_service.api.name
  role    = "roles/run.invoker"
  members = ["allUsers"]
}

resource "google_cloud_run_domain_mapping" "default" {
  name     = "douglas-cr-api.kvd.studio"
  location = var.gcp_region

  metadata {
    namespace = data.google_project.project.project_id
  }

  spec {
    route_name = google_cloud_run_v2_service.api.name
  }
}

resource "google_cloud_run_v2_job" "migrate" {
  name                = "db-migrations"
  location            = var.gcp_region
  deletion_protection = false

  template {
    parallelism = 1
    task_count  = 1

    template {
      timeout     = "120s"
      max_retries = 3

      containers {
        image = local.run_image
        command = ["/app/.venv/bin/alembic", "upgrade", "head"]

        resources {
          limits = {
            cpu    = "1"
            memory = "512Mi"
          }
        }

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
      }
    }
  }
}

resource "google_cloud_run_v2_job" "crawl" {
  name                = "douglas-crawler"
  location            = var.gcp_region
  deletion_protection = false

  template {
    parallelism = 1
    task_count  = 1

    template {
      timeout     = "120s"
      max_retries = 3

      containers {
        image = local.run_image
        command = ["/app/.venv/bin/python", "-m", "scripts.crawl"]

        resources {
          limits = {
            cpu    = "1"
            memory = "512Mi"
          }
        }

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
      }
    }
  }
}
