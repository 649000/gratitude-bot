data "aws_iam_policy_document" "ssm_read" {
  statement {
    effect = "Allow"
    actions = [
      "ssm:GetParametersByPath",
      "ssm:GetParameter",
      "ssm:GetParameters",
    ]
    resources = var.ssm_resource_arns
  }
}

data "aws_iam_policy_document" "kms_decrypt" {
  statement {
    effect    = "Allow"
    actions   = ["kms:Decrypt"]
    resources = ["*"]
  }
}

data "aws_iam_policy_document" "sqs_consume" {
  statement {
    effect = "Allow"
    actions = [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
    ]
    resources = [var.sqs_queue_arn]
  }
}

module "lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 8.0"

  function_name = "${var.project_name}-webhook-${var.environment}"
  description   = "Telegram webhook handler for ${var.project_name} (${var.environment})"
  handler       = "app.infrastructure.lambda_handler.handler"
  runtime       = var.runtime
  architectures = var.architectures
  memory_size   = var.memory_size
  timeout       = var.timeout
  publish       = true
  store_on_s3   = true
  s3_bucket     = var.s3_bucket

  source_path = [
    {
      path          = "${var.repo_root}/src/shared"
      prefix_in_zip = "shared"
    },
    {
      path          = "${var.repo_root}/src/app"
      prefix_in_zip = "app"
    },
    {
      pip_requirements = "${var.repo_root}/requirements.txt"
    },
  ]

  cloudwatch_logs_retention_in_days = var.log_retention_days

  environment_variables = merge(
    {
      APP_ENV   = var.environment
      DB_SCHEMA = var.db_schema
      LOG_LEVEL = var.log_level
    },
    var.additional_env_vars,
  )

  attach_policy_statements = true
  policy_statements = {
    ssm_read = {
      effect    = "Allow"
      actions   = ["ssm:GetParametersByPath", "ssm:GetParameter", "ssm:GetParameters"]
      resources = var.ssm_resource_arns
    }
    kms_decrypt = {
      effect    = "Allow"
      actions   = ["kms:Decrypt"]
      resources = ["*"]
    }
    sqs_read = {
      effect    = "Allow"
      actions   = ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"]
      resources = [var.sqs_queue_arn]
    }
  }

  allowed_triggers = {
    AllowExecutionFromSQS = {
      service    = "sqs"
      source_arn = var.sqs_queue_arn
    }
  }

  tags = var.tags
}

resource "aws_lambda_event_source_mapping" "webhook_sqs" {
  event_source_arn = var.sqs_queue_arn
  function_name    = module.lambda.lambda_function_arn
  batch_size       = 10
  enabled          = true
}
