output "ride_event_processor_arn" {
  description = "ARN of the Amazon MSK ride-event processor Lambda."
  value       = aws_lambda_function.ride_event_processor.arn
}

output "notification_worker_arn" {
  description = "ARN of the SQS-triggered notification worker Lambda."
  value       = aws_lambda_function.notification_worker.arn
}

output "processed_events_queue_url" {
  description = "URL of the SQS queue between the two Lambda functions."
  value       = aws_sqs_queue.processed_events.url
}

output "processed_events_dlq_arn" {
  description = "ARN of the dead-letter queue for repeatedly failing processed events."
  value       = aws_sqs_queue.processed_events_dlq.arn
}

output "ride_notifications_topic_arn" {
  description = "SNS topic that receives selected ride lifecycle notifications."
  value       = aws_sns_topic.ride_notifications.arn
}

output "operational_alerts_topic_arn" {
  description = "SNS topic used by CloudWatch operational alarms."
  value       = aws_sns_topic.operational_alerts.arn
}

output "cloudwatch_dashboard_name" {
  description = "Name of the CloudWatch serverless observability dashboard."
  value       = aws_cloudwatch_dashboard.serverless.dashboard_name
}

output "msk_event_source_enabled" {
  description = "Whether Terraform creates the Amazon MSK to Lambda event-source mapping."
  value       = var.msk_cluster_arn != null
}
