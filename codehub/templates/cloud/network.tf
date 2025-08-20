resource "google_compute_network" "network" {
  name = "${var.clustername}-network"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
  name = "${var.clustername}-subnet"
  region = var.region
  network = google_compute_network.network.id
  ip_cidr_range = "192.168.1.0/24"
  private_ip_google_access = true
}

resource "google_compute_router" "router" {
  name = "${var.clustername}-router"
  region = google_compute_subnetwork.subnet.region
  network = google_compute_network.network.id
}

resource "google_compute_router_nat" "nat-config" {
  name = "${var.clustername}-nat-config"
  region = google_compute_router.router.region
  router = google_compute_router.router.name
  nat_ip_allocate_option = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}

resource "google_compute_firewall" "allow-ssh" {
  name = "${var.clustername}-allow-ssh"
  network = google_compute_network.network.id
  source_ranges = ["35.235.240.0/20"]
  allow {
    protocol = "tcp"
    ports = [22]
  }
}
