terraform {
  required_providers {
    supabase = {
      source  = "supabase/supabase"
      version = "~>1.4.2"
    }
    google = {
      source  = "hashicorp/google"
      version = "~>6.12.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~>3.6.3"
    }
  }

  backend "gcs" {
    prefix = "douglas-crawler/tfstate"
  }
}
