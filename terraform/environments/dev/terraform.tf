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
      name    = "gratitude-bot-dev"
    }
  }
}
