output "digest_builder_arn" {
  description = "ARN of the digest builder Lambda"
  value       = module.digest_builder.lambda_function_arn
}

output "digest_builder_name" {
  description = "Name of the digest builder Lambda"
  value       = module.digest_builder.lambda_function_name
}

output "dispatcher_arn" {
  description = "ARN of the dispatcher Lambda"
  value       = module.dispatcher.lambda_function_arn
}

output "dispatcher_name" {
  description = "Name of the dispatcher Lambda"
  value       = module.dispatcher.lambda_function_name
}
