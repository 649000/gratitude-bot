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

variable "visibility_timeout" {
  description = "SQS visibility timeout in seconds"
  type        = number
  default     = 60
}

variable "max_receive_count" {
  description = "Maximum receive count before moving to DLQ"
  type        = number
  default     = 3
}

variable "dlq_retention_seconds" {
  description = "DLQ message retention in seconds"
  type        = number
  default     = 604800
}
