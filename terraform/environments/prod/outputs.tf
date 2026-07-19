output "api_gateway_url" {
  description = "API Gateway base URL"
  value       = module.api_gateway.api_endpoint
}

output "api_gateway_stage" {
  description = "API Gateway stage invoke URL"
  value       = module.api_gateway.stage_invoke_url
}

output "webhook_url" {
  description = "Full webhook URL to register with Telegram"
  value       = "${module.api_gateway.stage_invoke_url}api/v1/telegram/webhook"
}

output "lambda_function_name" {
  description = "Webhook Lambda function name"
  value       = module.webhook_lambda.lambda_function_name
}

output "lambda_function_arn" {
  description = "Webhook Lambda function ARN"
  value       = module.webhook_lambda.lambda_function_arn
}

output "lambda_role_arn" {
  description = "Lambda IAM role ARN"
  value       = module.webhook_lambda.lambda_role_arn
}
