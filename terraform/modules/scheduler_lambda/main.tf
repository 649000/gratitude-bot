locals {
  scheduler_source_path = [
    {
      path          = "${var.repo_root}/src/shared"
      prefix_in_zip = "shared"
    },
    {
      path          = "${var.repo_root}/src/scheduler/common"
      prefix_in_zip = "scheduler/common"
    },
    {
      pip_requirements = "${var.repo_root}/requirements.txt"
    },
  ]
}

# ── Digest Builder Lambda ──

module "digest_builder" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 8.0"

  function_name = "${var.project_name}-digest-builder-${var.environment}"
  description   = "Digest builder for ${var.project_name} (${var.environment})"
  handler       = "scheduler.digest_builder.handler.lambda_handler"
  runtime       = var.runtime
  architectures = var.architectures
  memory_size   = var.memory_size
  timeout       = var.scheduler_timeout
  publish       = true
  store_on_s3   = true
  s3_bucket     = var.s3_bucket

  source_path = concat(local.scheduler_source_path, [
    {
      path          = "${var.repo_root}/src/scheduler/digest_builder"
      prefix_in_zip = "scheduler/digest_builder"
    },
  ])

  cloudwatch_logs_retention_in_days = var.log_retention_days

  environment_variables = merge(
    {
      APP_ENV           = var.environment
      DB_SCHEMA         = var.db_schema
      LOG_LEVEL         = var.log_level
      DIGEST_SUMMARIZER = var.digest_summarizer
      BEDROCK_MODEL_ID  = var.bedrock_model_id
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
    bedrock_invoke = {
      effect    = "Allow"
      actions   = ["bedrock:InvokeModel"]
      resources = ["arn:aws:bedrock:*::foundation-model/*"]
    }
  }

  tags = merge(var.tags, { Service = "digest-builder" })
}

# ── Dispatcher Lambda ──

module "dispatcher" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 8.0"

  function_name = "${var.project_name}-dispatcher-${var.environment}"
  description   = "Scheduler dispatcher for ${var.project_name} (${var.environment})"
  handler       = "scheduler.dispatcher.handler.lambda_handler"
  runtime       = var.runtime
  architectures = var.architectures
  memory_size   = var.memory_size
  timeout       = var.scheduler_timeout
  publish       = true
  store_on_s3   = true
  s3_bucket     = var.s3_bucket

  source_path = concat(local.scheduler_source_path, [
    {
      path          = "${var.repo_root}/src/scheduler/dispatcher"
      prefix_in_zip = "scheduler/dispatcher"
    },
  ])

  cloudwatch_logs_retention_in_days = var.log_retention_days

  environment_variables = merge(
    {
      APP_ENV       = var.environment
      DB_SCHEMA     = var.db_schema
      LOG_LEVEL     = var.log_level
      SQS_QUEUE_URL = var.sqs_queue_url
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
    sqs_send = {
      effect    = "Allow"
      actions   = ["sqs:SendMessage"]
      resources = [var.sqs_queue_arn]
    }
  }

  tags = merge(var.tags, { Service = "dispatcher" })
}
