resource "google_container_cluster" "cluster" {
  name     = var.clustername
  location = var.region

  network = google_compute_network.network.id
  subnetwork = google_compute_subnetwork.subnet.id

  # We can't create a cluster with no node pool defined, but we want to only use
  # separately managed node pools. So we create the smallest possible default
  # node pool and immediately delete it.
  remove_default_node_pool = true
  initial_node_count       = 1

  networking_mode = "VPC_NATIVE"

  private_cluster_config {
    enable_private_nodes = true
    master_ipv4_cidr_block = "172.16.0.32/28"
  }

  master_auth {
    client_certificate_config {
      issue_client_certificate = false
    }
  }

  deletion_protection = false
}

resource "google_container_node_pool" "default" {
  name       = "default-pool"
  location = google_container_cluster.cluster.location
  cluster    = google_container_cluster.cluster.name
  initial_node_count = 1

  lifecycle {
    ignore_changes = [initial_node_count]
  }

  autoscaling {
    min_node_count = var.min_nodes
    max_node_count = var.max_nodes
  }

  node_config {
    machine_type = var.machine_type
    disk_size_gb = 30
    disk_type = "pd-standard"
  }
}
