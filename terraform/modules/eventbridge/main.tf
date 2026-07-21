resource "aws_cloudwatch_event_rule" "digest_weekly" {
  name                = "${var.project_name}-digest-weekly-${var.environment}"
  description         = "Trigger weekly digest generation"
  schedule_expression = var.digest_weekly_schedule
  tags                = var.tags
}

resource "aws_cloudwatch_event_target" "digest_weekly" {
  rule      = aws_cloudwatch_event_rule.digest_weekly.name
  target_id = "digest-builder"
  arn       = var.digest_builder_lambda_arn
  input     = jsonencode({ type = "weekly" })
}

resource "aws_lambda_permission" "digest_weekly" {
  statement_id  = "AllowEventBridgeDigestWeekly"
  action        = "lambda:InvokeFunction"
  function_name = var.digest_builder_lambda_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.digest_weekly.arn
}

resource "aws_cloudwatch_event_rule" "digest_monthly" {
  name                = "${var.project_name}-digest-monthly-${var.environment}"
  description         = "Trigger monthly digest generation"
  schedule_expression = var.digest_monthly_schedule
  tags                = var.tags
}

resource "aws_cloudwatch_event_target" "digest_monthly" {
  rule      = aws_cloudwatch_event_rule.digest_monthly.name
  target_id = "digest-builder"
  arn       = var.digest_builder_lambda_arn
  input     = jsonencode({ type = "monthly" })
}

resource "aws_lambda_permission" "digest_monthly" {
  statement_id  = "AllowEventBridgeDigestMonthly"
  action        = "lambda:InvokeFunction"
  function_name = var.digest_builder_lambda_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.digest_monthly.arn
}

resource "aws_cloudwatch_event_rule" "digest_yearly" {
  name                = "${var.project_name}-digest-yearly-${var.environment}"
  description         = "Trigger yearly digest generation"
  schedule_expression = var.digest_yearly_schedule
  tags                = var.tags
}

resource "aws_cloudwatch_event_target" "digest_yearly" {
  rule      = aws_cloudwatch_event_rule.digest_yearly.name
  target_id = "digest-builder"
  arn       = var.digest_builder_lambda_arn
  input     = jsonencode({ type = "yearly" })
}

resource "aws_lambda_permission" "digest_yearly" {
  statement_id  = "AllowEventBridgeDigestYearly"
  action        = "lambda:InvokeFunction"
  function_name = var.digest_builder_lambda_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.digest_yearly.arn
}

resource "aws_cloudwatch_event_rule" "dispatch_tick" {
  name                = "${var.project_name}-dispatch-tick-${var.environment}"
  description         = "Trigger dispatcher every hour"
  schedule_expression = var.dispatch_schedule
  tags                = var.tags
}

resource "aws_cloudwatch_event_target" "dispatch_tick" {
  rule      = aws_cloudwatch_event_rule.dispatch_tick.name
  target_id = "dispatcher"
  arn       = var.dispatcher_lambda_arn
}

resource "aws_lambda_permission" "dispatch_tick" {
  statement_id  = "AllowEventBridgeDispatchTick"
  action        = "lambda:InvokeFunction"
  function_name = var.dispatcher_lambda_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.dispatch_tick.arn
}
