provider "supabase" {
  access_token = var.supabase_access_token
}

provider "google" {
  project = var.project
  region  = var.gcp_region
}

provider "random" {}
