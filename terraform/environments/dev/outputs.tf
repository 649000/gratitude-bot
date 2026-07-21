output "webhook_url" {
  description = "Full webhook URL to register with Telegram"
  value       = "${module.apigw.stage_invoke_url}api/v1/telegram/webhook"
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
  description = "Webhook Lambda IAM role ARN"
  value       = module.webhook_lambda.lambda_role_arn
}
