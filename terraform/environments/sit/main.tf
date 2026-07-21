module "s3" {
  source = "../../modules/s3"

  environment = var.environment
  tags        = local.common_tags
}

module "sqs" {
  source = "../../modules/sqs"

  project_name = local.project_name
  environment  = var.environment
  tags         = local.common_tags
}

module "ssm" {
  source = "../../modules/ssm"

  project_name       = local.project_name
  environment        = var.environment
  telegram_bot_token = var.telegram_bot_token
  database_url       = var.database_url
  tags               = local.common_tags
}

module "webhook_lambda" {
  source = "../../modules/webhook_lambda"

  project_name      = local.project_name
  environment       = var.environment
  repo_root         = "${local.repo_root}/../../.."
  architectures     = ["arm64"]
  memory_size       = var.lambda_memory_size
  timeout           = var.lambda_timeout
  log_retention_days = 14
  log_level         = var.log_level
  db_schema         = var.db_schema
  s3_bucket         = module.s3.bucket
  ssm_resource_arns = local.ssm_resource_arns
  sqs_queue_arn     = module.sqs.queue_arn
  tags              = merge(local.common_tags, { Service = "telegram-webhook" })
}

resource "aws_lambda_permission" "apigw_invoke" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = module.webhook_lambda.lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${module.apigw.api_execution_arn}/*/*"
}

module "scheduler_lambda" {
  source = "../../modules/scheduler_lambda"

  project_name      = local.project_name
  environment       = var.environment
  repo_root         = "${local.repo_root}/../../.."
  architectures     = ["arm64"]
  memory_size       = var.lambda_memory_size
  log_retention_days = 14
  log_level         = var.log_level
  db_schema         = var.db_schema
  digest_summarizer = var.digest_summarizer
  bedrock_model_id  = var.bedrock_model_id
  s3_bucket         = module.s3.bucket
  ssm_resource_arns = local.ssm_resource_arns
  sqs_queue_arn     = module.sqs.queue_arn
  sqs_queue_url     = module.sqs.queue_url
  tags              = local.common_tags
}

module "apigw" {
  source = "../../modules/apigw"

  project_name        = local.project_name
  environment         = var.environment
  webhook_lambda_arn  = module.webhook_lambda.lambda_function_arn
  log_retention_days  = 14
  tags                = local.common_tags
}

module "eventbridge" {
  source = "../../modules/eventbridge"

  project_name                = local.project_name
  environment                 = var.environment
  digest_builder_lambda_arn   = module.scheduler_lambda.digest_builder_arn
  digest_builder_lambda_name  = module.scheduler_lambda.digest_builder_name
  dispatcher_lambda_arn       = module.scheduler_lambda.dispatcher_arn
  dispatcher_lambda_name      = module.scheduler_lambda.dispatcher_name
  tags                        = local.common_tags
}
