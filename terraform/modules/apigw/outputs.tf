output "api_endpoint" {
  description = "API Gateway base URL"
  value       = module.api_gateway.api_endpoint
}

output "stage_invoke_url" {
  description = "API Gateway stage invoke URL"
  value       = module.api_gateway.stage_invoke_url
}

output "api_execution_arn" {
  description = "API Gateway execution ARN"
  value       = module.api_gateway.api_execution_arn
}
