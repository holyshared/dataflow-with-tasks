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
    "dataflow.googleapis.com",
    "logging.googleapis.com",
    "storage.googleapis.com",
  ]
}
