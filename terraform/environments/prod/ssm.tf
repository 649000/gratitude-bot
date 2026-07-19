resource "aws_ssm_parameter" "telegram_bot_token" {
  name        = "${local.ssm_path}/telegram_bot_token"
  description = "Telegram bot token for ${var.environment}"
  type        = "SecureString"
  value       = var.telegram_bot_token

  tags = local.common_tags
}

resource "aws_ssm_parameter" "database_url" {
  name        = "${local.ssm_path}/database_url"
  description = "Database URL for ${var.environment}"
  type        = "SecureString"
  value       = var.database_url

  tags = local.common_tags
}
