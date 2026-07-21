variable "project_name" {
  description = "Project name used in resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, sit, prod)"
  type        = string
}

variable "repo_root" {
  description = "Path to the repository root (for source_path resolution)"
  type        = string
}

variable "runtime" {
  description = "Lambda runtime"
  type        = string
  default     = "python3.12"
}

variable "architectures" {
  description = "Lambda architectures"
  type        = list(string)
  default     = ["x86_64"]
}

variable "memory_size" {
  description = "Lambda memory in MB"
  type        = number
  default     = 256
}

variable "timeout" {
  description = "Lambda timeout in seconds"
  type        = number
  default     = 30
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 7
}

variable "log_level" {
  description = "Application log level"
  type        = string
  default     = "DEBUG"
}

variable "db_schema" {
  description = "Database schema"
  type        = string
  default     = "gratitude_bot"
}

variable "s3_bucket" {
  description = "S3 bucket for Lambda package storage"
  type        = string
}

variable "ssm_resource_arns" {
  description = "SSM parameter ARNs the Lambda can access"
  type        = list(string)
}

variable "sqs_queue_arn" {
  description = "SQS queue ARN for outgoing messages"
  type        = string
}

variable "tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
}

variable "additional_env_vars" {
  description = "Additional environment variables"
  type        = map(string)
  default     = {}
}
