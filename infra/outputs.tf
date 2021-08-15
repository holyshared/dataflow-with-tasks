output "credentials" {
  value = base64decode(google_service_account_key.dataflow_key.private_key)
  sensitive = true
}

output "vpc_network_name" {
  value = google_compute_network.vpc_network.name
}
