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
      path             = "${path.module}/../../.."
      pip_requirements = "${path.module}/../../../requirements.txt"
      patterns = [
        "!\\.git/.*",
        "!terraform/.*",
        "!alembic/.*",
        "!alembic\\.ini",
        "!\\.githooks/.*",
        "!\\.idea/.*",
        "!\\.env.*",
        "!\\.python-version",
        "!pyproject\\.toml",
        "!uv\\.lock",
      ]
    }
  ]

  cloudwatch_logs_retention_in_days = 14

  environment_variables = {
    APP_ENV   = var.environment
    DB_SCHEMA = var.db_schema
    LOG_LEVEL = var.log_level
  }

  attach_policy_statements = true
  policy_statements = {
    ssm_read = {
      effect    = "Allow"
      actions   = [
        "ssm:GetParametersByPath",
        "ssm:GetParameter",
        "ssm:GetParameters"
      ]
      resources = [
        "arn:aws:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:parameter${local.ssm_path}",
        "arn:aws:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:parameter${local.ssm_path}/*"
      ]
    }
    kms_decrypt = {
      effect    = "Allow"
      actions   = ["kms:Decrypt"]
      resources = ["*"]
    }
    sqs_read = {
      effect    = "Allow"
      actions   = [
        "sqs:ReceiveMessage",
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes",
      ]
      resources = [aws_sqs_queue.outgoing.arn]
    }
  }

  allowed_triggers = {
    AllowExecutionFromAPIGateway = {
      service    = "apigateway"
      source_arn = "${module.api_gateway.api_execution_arn}/*/*"
    }
    AllowExecutionFromSQS = {
      service    = "sqs"
      source_arn = aws_sqs_queue.outgoing.arn
    }
  }

  tags = local.common_tags
}

resource "aws_lambda_event_source_mapping" "webhook_sqs" {
  event_source_arn = aws_sqs_queue.outgoing.arn
  function_name    = module.webhook_lambda.lambda_function_arn
  batch_size       = 10
  enabled          = true
}
