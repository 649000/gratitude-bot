module "api_gateway" {
  source  = "terraform-aws-modules/apigateway-v2/aws"
  version = "~> 5.0"

  name          = "${var.project_name}-webhook-${var.environment}"
  description   = "HTTP API Gateway for ${var.project_name} Telegram webhook"
  protocol_type = "HTTP"
  create_domain_name = var.create_domain_name

  cors_configuration = {
    allow_headers = ["Content-Type", "Authorization"]
    allow_methods = ["*"]
    allow_origins = ["*"]
    max_age       = 300
  }

  stage_access_log_settings = {
    create_log_group            = true
    log_group_retention_in_days = var.log_retention_days
    format = jsonencode({
      context = {
        domainName              = "$context.domainName"
        integrationErrorMessage = "$context.integrationErrorMessage"
        protocol                = "$context.protocol"
        requestId               = "$context.requestId"
        requestTime             = "$context.requestTime"
        responseLength          = "$context.responseLength"
        routeKey                = "$context.routeKey"
        stage                   = "$context.stage"
        status                  = "$context.status"
        error = {
          message      = "$context.error.message"
          responseType = "$context.error.responseType"
        }
        identity = {
          sourceIP = "$context.identity.sourceIp"
        }
        integration = {
          error             = "$context.integration.error"
          integrationStatus = "$context.integration.integrationStatus"
        }
      }
    })
  }

  routes = {
    "$default" = {
      integration = {
        uri                    = var.webhook_lambda_arn
        payload_format_version = "2.0"
        timeout_milliseconds   = var.integration_timeout_ms
      }
    }
  }

  tags = var.tags
}
