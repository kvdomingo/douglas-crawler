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
