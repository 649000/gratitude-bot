resource "aws_ssm_parameter" "telegram_bot_token" {
  name        = "/${var.project_name}/${var.environment}/telegram_bot_token"
  description = "Telegram bot token for ${var.environment}"
  type        = "SecureString"
  value       = var.telegram_bot_token
  tags        = var.tags
}

resource "aws_ssm_parameter" "database_url" {
  name        = "/${var.project_name}/${var.environment}/database_url"
  description = "Database URL for ${var.environment}"
  type        = "SecureString"
  value       = var.database_url
  tags        = var.tags
}
