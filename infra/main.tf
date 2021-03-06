terraform {
  required_providers {
    google-beta = {
      source  = "hashicorp/google"
      version = "3.79.0"
    }
  }
}

provider "google-beta" {
  region = var.location
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
    "cloudbuild.googleapis.com",
    "cloudfunctions.googleapis.com",
    "cloudtasks.googleapis.com"
  ]
}

resource "google_service_account" "dataflow_service_account" {
  project      = module.project-factory.project_id
  account_id   = "dataflow-example"
  display_name = "dataflow for example"
}

resource "google_project_iam_member" "dataflow_service_account_user" {
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

resource "google_project_iam_member" "dataflow_object_manager" {
  project = module.project-factory.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.dataflow_service_account.email}"
}

resource "google_project_iam_member" "dataflow_task_enqueuer" {
  project = module.project-factory.project_id
  role    = "roles/cloudtasks.enqueuer"
  member  = "serviceAccount:${google_service_account.dataflow_service_account.email}"
}


# Function invoker
resource "google_service_account" "dataflow_function_service_account" {
  project      = module.project-factory.project_id
  account_id   = "dataflow-function-invoker"
  display_name = "dataflow for cloud tasks"
}

resource "google_project_iam_member" "function_invoker_service_account_user" {
  project = module.project-factory.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.dataflow_function_service_account.email}"
}

resource "google_project_iam_member" "function_invoker" {
  project = module.project-factory.project_id
  role    = "roles/cloudfunctions.invoker"
  member  = "serviceAccount:${google_service_account.dataflow_function_service_account.email}"
}

resource "google_project_iam_member" "cloudbuild_cloud_functions_developer" {
  project = module.project-factory.project_id
  role    = "roles/cloudfunctions.developer"
  member  = "serviceAccount:${module.project-factory.project_number}@cloudbuild.gserviceaccount.com"
}

resource "google_project_iam_member" "cloudbuild_service_account_user" {
  project = module.project-factory.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${module.project-factory.project_number}@cloudbuild.gserviceaccount.com"
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

resource "google_compute_firewall" "dataflow_firewall" {
  project  = module.project-factory.project_id
  name    = "dataflow-firewall"
  network = google_compute_network.vpc_network.name

  direction = "INGRESS"

  allow {
    protocol = "tcp"
    ports    = ["12345-12346"]
  }

  priority = 0

  target_tags = ["dataflow"]
  source_tags = ["dataflow"]
}

resource "google_storage_bucket" "logs" {
  project  = module.project-factory.project_id
  name     = "logs-${module.project-factory.project_id}"
  location = var.location

  force_destroy = true
}

resource "google_storage_bucket" "flex_templates" {
  project  = module.project-factory.project_id
  name     = "flex-templates-${module.project-factory.project_id}"
  location = var.location

  force_destroy = true
}

resource "google_cloudbuild_trigger" "flex_template_trigger" {
  name = "dataflow-cloud-tasks"
  project = module.project-factory.project_id

  github {
    name  = "dataflow-with-tasks"
    owner = "holyshared"

    push {
      branch       = "main"
      invert_regex = false
    }
  }

  substitutions = {
    _PROJECT_ID=module.project-factory.project_id
    _REGION=var.location
    _IMAGE_NAME="dataflow_cloud_tasks"
    _TEMPLATE_PATH="gs://${google_storage_bucket.flex_templates.name}/dataflow/flex_templates/cloud_tasks.json"
    _SERVICE_ACCOUNT_EMAIL=google_service_account.dataflow_service_account.email
  }

  filename = "flex-template.cloudbuild.yml"
}

resource "google_cloudbuild_trigger" "function_trigger" {
  name = "task-functions"
  project = module.project-factory.project_id

  github {
    name  = "dataflow-with-tasks"
    owner = "holyshared"

    push {
      branch       = "main"
      invert_regex = false
    }
  }

  substitutions = {
    _PROJECT_ID=module.project-factory.project_id
    _REGION=var.location
    _SERVICE_ACCOUNT_EMAIL=google_service_account.dataflow_function_service_account.email
  }

  filename = "function.cloudbuild.yml"
}

resource "google_cloud_tasks_queue" "dataflow_queue" {
  name = "dataflow-queue"
  project = module.project-factory.project_id
  location = var.location
  depends_on = [
    google_app_engine_application.dataflow_app
  ]
}

resource "google_app_engine_application" "dataflow_app" {
  project = module.project-factory.project_id
  location_id = var.location
}
