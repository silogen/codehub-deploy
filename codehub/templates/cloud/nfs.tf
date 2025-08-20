resource "google_filestore_instance" "nfs" {
  name = "${var.clustername}-fsid"
  location = var.zone
  tier = "STANDARD"

  file_shares {
    capacity_gb = 1024
    name = "${var.clustername}fs"
  }

  networks {
    network = google_compute_network.network.name
    modes = ["MODE_IPV4"]
  }
}
