variable "gcp_project_name" {
  type = string
  description = "Name of the gcp project that deploys the resources."
}
variable "clustername" {
  type = string
  description = "Name of the cluster, typically `<customer><cohortid>`, e.g. `ads18`"
}

variable "region" {
  type = string
  description = "Region to deploy resources in"
}

variable "zone" {
  type = string
  description = "Specific zone in region"
}

variable "machine_type" {
  type = string
  description = "VM type to use for cluster nodes"
}

variable gcp_sa_path {
  type = string
  description = "Path to Service Account credentials"
}

variable "min_nodes" {
  type = number
  default = 1
  description = "Minimum number of nodes per zone"
}

variable "max_nodes" {
  type = number
  default = 100
  description = "Maximum number of nodes per zone"
}
