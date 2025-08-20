provider "google" {
  project = var.gcp_project_name
  region = var.region
  zone = var.zone
  credentials = var.gcp_sa_path
}

data "google_client_config" "current" {}
