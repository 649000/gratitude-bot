module "api_gateway" {
  source  = "terraform-aws-modules/apigateway-v2/aws"
  version = "~> 5.0"

  name          = "${local.project_name}-webhook-${var.environment}"
  description   = "HTTP API Gateway for ${local.project_name} Telegram webhook"
  protocol_type = "HTTP"

  cors_configuration = {
    allow_headers = ["Content-Type", "Authorization"]
    allow_methods = ["*"]
    allow_origins = ["*"]
    max_age       = 300
  }

  # Access logs
  stage_access_log_settings = {
    create_log_group            = true
    log_group_retention_in_days = 7
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

  # Routes & Integrations
  routes = {
    "$default" = {
      integration = {
        uri                    = module.webhook_lambda.lambda_function_arn
        payload_format_version = "2.0"
        timeout_milliseconds   = 30000
      }
    }
  }

  tags = local.common_tags
}
