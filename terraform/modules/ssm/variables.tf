variable "project_name" {
  description = "Project name used in SSM path"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, sit, prod)"
  type        = string
}

variable "telegram_bot_token" {
  description = "Telegram bot token"
  type        = string
  sensitive   = true
}

variable "database_url" {
  description = "Database connection URL"
  type        = string
  sensitive   = true
}

variable "tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
}
