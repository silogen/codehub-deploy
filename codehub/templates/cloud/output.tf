output "nfs_name" {
  value = google_filestore_instance.nfs.file_shares[0].name
}
output "nfs_ip" {
  value = google_filestore_instance.nfs.networks[0].ip_addresses[0]
}
output "cluster_id" {
  value = google_container_cluster.cluster.id
}
output "hub_sa_key" {
  value = base64decode(google_service_account_key.docker_auth.private_key)
  description = <<EOT
    Key for SA used for pulling images in the hub.
    The SA has minimum permissions, so the key is not extremely sensitive.
  EOT
  sensitive = true
}
output "cluster_endpoint" {
  value = google_container_cluster.cluster.endpoint
}
output "cluster_cert" {
  value = google_container_cluster.cluster.master_auth[0].cluster_ca_certificate
  sensitive = true
}
output "gcp_token" {
  value = data.google_client_config.current.access_token
  sensitive = true
}
output "docker_registry_hostname" {
  value = "https://${data.google_artifact_registry_repository.docker.location}-docker.pkg.dev"
  description = "Docker registry hostname where JupyterHub images are stored."
}
output "docker_image" {
  // Remove hash from the self_link
  value = split(
    "@",
    data.google_artifact_registry_docker_image.jupyter-env.self_link
  )[0]
  description = "Docker image with JupyterHub environment."
}
