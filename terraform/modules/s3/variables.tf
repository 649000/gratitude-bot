variable "environment" {
  description = "Environment name (dev, sit, prod)"
  type        = string
}

variable "tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
}
