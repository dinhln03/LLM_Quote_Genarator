# Ref: https://github.com/terraform-google-modules/terraform-google-kubernetes-engine/blob/master/examples/simple_autopilot_public
# To define that we will use GCP
terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "4.80.0" // Provider version
    }
  }
  required_version = "1.9.8" // Terraform version
}

// The library with methods for creating and
// managing the infrastructure in GCP, this will
// apply to all the resources in the project
provider "google" {
  project     = var.project_id
  region      = var.region
}

// Google Cloud Storage
// https://cloud.google.com/storage/docs/terraform-create-bucket-upload-object
// or refer to https://registry.terraform.io/providers/hashicorp/google/latest/docs
# resource "google_storage_bucket" "static" {
#   name          = var.bucket
#   location      = var.region

#   # Enable bucket level access
#   uniform_bucket_level_access = true
# }

# // Google Compute Engine
# resource "google_compute_instance" "vm_instance" {
#   name         = "terraform-instance"
#   machine_type = "e2-micro"
#   zone         = "us-central1-c"

#   // This instances use ubuntu image
#   boot_disk {
#     initialize_params {
#       image = "projects/ubuntu-os-cloud/global/images/ubuntu-2204-jammy-v20230727"
#     }
#   }

#   // Default network for the instance
#   network_interface {
#     network = "default"
#     access_config {}
#   }
# }

// Google Kubernetes Engine
resource "google_container_cluster" "primary" {
  name     = "${var.project_id}-gke"
  location = var.region
  remove_default_node_pool = true
  initial_node_count       = 1

}

resource "google_container_node_pool" "primary_preemptible_nodes" {
  name       = "${var.project_id}-node-pool"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  node_count = 2

  node_config {
    machine_type = "e2-standard-4"
    disk_size_gb = 60
  }

  autoscaling {
    min_node_count = 1
    max_node_count = 2
  }
}
