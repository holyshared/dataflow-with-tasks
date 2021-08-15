terraform {
  required_providers {
    google-beta = {
      source  = "hashicorp/google"
      version = "3.79.0"
    }
  }
}

provider "google-beta" {
  region = "asia-northeast1"
}

module "project-factory" {
  source  = "terraform-google-modules/project-factory/google"
  version = "11.1.1"

  name              = "dataflow-with-tasks"
  random_project_id = true
  org_id            = var.org_id
  billing_account   = var.billing_account
  folder_id         = var.folder_id

  activate_apis = [
    "iam.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "compute.googleapis.com",
    "dataflow.googleapis.com",
    "logging.googleapis.com",
    "storage.googleapis.com",
  ]
}

resource "google_service_account" "dataflow_service_account" {
  project      = module.project-factory.project_id
  account_id   = "dataflow-example"
  display_name = "dataflow for example"
}

resource "google_project_iam_member" "service_account_user" {
  project = module.project-factory.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.dataflow_service_account.email}"
}

resource "google_project_iam_member" "dataflow_developer" {
  project = module.project-factory.project_id
  role    = "roles/dataflow.developer"
  member  = "serviceAccount:${google_service_account.dataflow_service_account.email}"
}

resource "google_project_iam_member" "dataflow_worker" {
  project = module.project-factory.project_id
  role    = "roles/dataflow.worker"
  member  = "serviceAccount:${google_service_account.dataflow_service_account.email}"
}

resource "google_project_iam_member" "object_manager" {
  project = module.project-factory.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.dataflow_service_account.email}"
}

resource "time_rotating" "dataflow_key_rotation" {
  rotation_days = 30
}

resource "google_service_account_key" "dataflow_key" {
  service_account_id = google_service_account.dataflow_service_account.name

  keepers = {
    rotation_time = time_rotating.dataflow_key_rotation.rotation_rfc3339
  }
}

resource "google_compute_network" "vpc_network" {
  project  = module.project-factory.project_id
  name = "dataflow-vpc-network"
}

resource "google_storage_bucket" "logs" {
  project  = module.project-factory.project_id
  name     = "logs-${module.project-factory.project_id}"
  location = "asia-northeast1"

  force_destroy = true
}
