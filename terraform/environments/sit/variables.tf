variable "environment" {
  description = "Environment name"
  type        = string
  default     = "sit"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "ap-southeast-1"
}

variable "database_url" {
  description = "Database connection URL"
  type        = string
  sensitive   = true
}

variable "telegram_bot_token" {
  description = "Telegram bot token"
  type        = string
  sensitive   = true
  default     = ""
}

variable "lambda_memory_size" {
  description = "Lambda memory in MB"
  type        = number
  default     = 256
}

variable "lambda_timeout" {
  description = "Lambda timeout in seconds"
  type        = number
  default     = 30
}

variable "log_level" {
  description = "Application log level"
  type        = string
  default     = "INFO"
}

variable "db_schema" {
  description = "Database schema"
  type        = string
  default     = "gratitude_bot"
}
