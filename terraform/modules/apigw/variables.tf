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

variable "webhook_lambda_arn" {
  description = "ARN of the webhook Lambda function"
  type        = string
}

variable "create_domain_name" {
  description = "Whether to create a custom domain name"
  type        = bool
  default     = false
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 7
}

variable "integration_timeout_ms" {
  description = "API Gateway integration timeout in milliseconds"
  type        = number
  default     = 30000
}
