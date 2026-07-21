variable "project_name" {
  description = "Project name used in resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, sit, prod)"
  type        = string
}

variable "tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
}

variable "digest_builder_lambda_arn" {
  description = "ARN of the digest builder Lambda"
  type        = string
}

variable "digest_builder_lambda_name" {
  description = "Name of the digest builder Lambda"
  type        = string
}

variable "dispatcher_lambda_arn" {
  description = "ARN of the dispatcher Lambda"
  type        = string
}

variable "dispatcher_lambda_name" {
  description = "Name of the dispatcher Lambda"
  type        = string
}

variable "digest_weekly_schedule" {
  description = "EventBridge schedule expression for weekly digest"
  type        = string
  default     = "cron(0 12 ? * SUN *)"
}

variable "digest_monthly_schedule" {
  description = "EventBridge schedule expression for monthly digest"
  type        = string
  default     = "cron(0 12 L * ? *)"
}

variable "digest_yearly_schedule" {
  description = "EventBridge schedule expression for yearly digest"
  type        = string
  default     = "cron(0 12 31 12 ? *)"
}

variable "dispatch_schedule" {
  description = "EventBridge schedule expression for dispatcher"
  type        = string
  default     = "rate(1 hour)"
}
