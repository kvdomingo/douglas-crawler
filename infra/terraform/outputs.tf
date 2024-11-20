output "supabase_database_password" {
  value     = random_password.supabase_password.result
  sensitive = true
}
