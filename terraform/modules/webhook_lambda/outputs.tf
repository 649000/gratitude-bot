output "lambda_function_arn" {
  description = "ARN of the webhook Lambda function"
  value       = module.lambda.lambda_function_arn
}

output "lambda_function_name" {
  description = "Name of the webhook Lambda function"
  value       = module.lambda.lambda_function_name
}

output "lambda_role_arn" {
  description = "IAM role ARN of the webhook Lambda"
  value       = module.lambda.lambda_role_arn
}

output "lambda_role_name" {
  description = "IAM role name of the webhook Lambda"
  value       = module.lambda.lambda_role_name
}
