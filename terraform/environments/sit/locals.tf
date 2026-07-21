data "aws_caller_identity" "current" {}

locals {
  project_name = "gratitude-bot"
  ssm_path     = "/${local.project_name}/${var.environment}"

  common_tags = {
    Project     = local.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }

  ssm_resource_arns = [
    "arn:aws:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:parameter${local.ssm_path}",
    "arn:aws:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:parameter${local.ssm_path}/*",
  ]

  repo_root = path.module
}
