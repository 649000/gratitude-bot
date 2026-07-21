resource "aws_sqs_queue" "outgoing" {
  name                       = "${var.project_name}-outgoing-${var.environment}"
  delay_seconds              = 0
  max_message_size           = 262144
  message_retention_seconds  = 86400
  receive_wait_time_seconds  = 0
  visibility_timeout_seconds = var.visibility_timeout

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.outgoing_dlq.arn
    maxReceiveCount     = var.max_receive_count
  })

  tags = var.tags
}

resource "aws_sqs_queue" "outgoing_dlq" {
  name                      = "${var.project_name}-outgoing-dlq-${var.environment}"
  message_retention_seconds = var.dlq_retention_seconds

  tags = var.tags
}
