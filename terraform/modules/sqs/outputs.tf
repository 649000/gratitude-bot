output "queue_arn" {
  description = "ARN of the outgoing SQS queue"
  value       = aws_sqs_queue.outgoing.arn
}

output "queue_url" {
  description = "URL of the outgoing SQS queue"
  value       = aws_sqs_queue.outgoing.url
}
