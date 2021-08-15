output "dataflow_credentials" {
  value = base64decode(google_service_account_key.dataflow_key.private_key)
  sensitive = true
}

output "dataflow_service_account_email" {
  value = google_service_account.dataflow_service_account.email
}

output "dataflow_vpc_network_name" {
  value = google_compute_network.vpc_network.name
}

output "dataflow_bucket_name" {
  value = google_storage_bucket.logs.name
}
