variable "project" {
  type = string
}

variable "gcp_region" {
  type = string
}

variable "supabase_region" {
  type = string
}

variable "supabase_access_token" {
  type      = string
  sensitive = true
}

variable "supabase_organization_id" {
  type = string
}

variable "github_repo_id" {
  type = string
}
