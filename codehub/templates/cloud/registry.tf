data "google_artifact_registry_repository" "docker" {
  location = var.region
  repository_id = "codehub"
}

data "google_artifact_registry_docker_image" "jupyter-env" {
  location = data.google_artifact_registry_repository.docker.location
  repository_id = data.google_artifact_registry_repository.docker.repository_id
  image_name = "jupyter-env"
}

resource "google_service_account" "docker_auth" {
  account_id   = "${var.clustername}-docker-auth"
  display_name = "${var.clustername} Docker Authentication Service Account"
  description = "SA with minimal permissions to pull images from Artifact Registry, for use in JupyterHub"
}

resource "google_artifact_registry_repository_iam_binding" "docker_reader" {
  location     = data.google_artifact_registry_repository.docker.location
  repository   = data.google_artifact_registry_repository.docker.repository_id
  role         = "roles/artifactregistry.reader"

  members = [
    "serviceAccount:${google_service_account.docker_auth.email}"
  ]
}

resource "google_service_account_key" "docker_auth" {
  service_account_id = google_service_account.docker_auth.id
}
