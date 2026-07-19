module "webhook_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 8.0"

  function_name = "${local.project_name}-webhook-${var.environment}"
  description   = "Telegram webhook handler for ${local.project_name} (${var.environment})"
  handler       = "app.infrastructure.lambda_handler.handler"
  runtime       = "python3.12"
  architectures = ["arm64"]
  memory_size   = var.lambda_memory_size
  timeout       = var.lambda_timeout
  publish       = true
  store_on_s3   = true
  s3_bucket     = aws_s3_bucket.lambda_packages.bucket

  source_path = [
    {
      path             = "${path.module}/../../../app"
      pip_requirements = "${path.module}/../../../requirements.txt"
    }
  ]

  cloudwatch_logs_retention_in_days = 30

  environment_variables = {
    APP_ENV   = var.environment
    DB_SCHEMA = var.db_schema
    LOG_LEVEL = var.log_level
  }

  attach_policy_statements = true
  policy_statements = {
    ssm_read = {
      effect    = "Allow"
      actions   = ["ssm:GetParameters", "ssm:GetParameter"]
      resources = ["arn:aws:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:parameter${local.ssm_path}/*"]
    }
  }

  allowed_triggers = {
    AllowExecutionFromAPIGateway = {
      service    = "apigateway"
      source_arn = "${module.api_gateway.api_execution_arn}/*/*"
    }
  }

  tags = local.common_tags
}
