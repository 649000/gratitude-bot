terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 6.28.0"
    }
    random = {
      source  = "hashicorp/random"
      version = ">= 3.0"
    }
  }

  cloud {
    organization = "nas-personal-projects"
    workspaces {
      project = "gratitude-bot"
      name    = "gratitude-bot-prod"
    }
  }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project     = "gratitude-bot"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

data "aws_caller_identity" "current" {}

locals {
  project_name = "gratitude-bot"
  ssm_path     = "/${local.project_name}/${var.environment}"

  common_tags = {
    Project     = local.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
    Service     = "telegram-webhook"
  }
}
