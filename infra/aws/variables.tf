variable "aws_region" {
  description = "AWS region for the serverless extension."
  type        = string
  default     = "us-east-1"
}

variable "name_prefix" {
  description = "Resource-name prefix used by the reference deployment."
  type        = string
  default     = "ride-sharing"
}

variable "msk_cluster_arn" {
  description = "Optional Amazon MSK cluster ARN. When null, the MSK event source mapping is not created."
  type        = string
  default     = null
  nullable    = true
}

variable "ride_events_topic" {
  description = "Kafka topic consumed by the ride-event processor Lambda."
  type        = string
  default     = "ride.events"
}

variable "consumer_group_id" {
  description = "Consumer group used by the Lambda Amazon MSK event source mapping."
  type        = string
  default     = "ride-sharing-lambda"
}

variable "lambda_memory_mb" {
  description = "Memory allocated to each Lambda function."
  type        = number
  default     = 256

  validation {
    condition     = var.lambda_memory_mb >= 128 && var.lambda_memory_mb <= 10240
    error_message = "lambda_memory_mb must be between 128 and 10240."
  }
}

variable "log_retention_days" {
  description = "CloudWatch Logs retention period for Lambda log groups."
  type        = number
  default     = 14
}

variable "alarm_email" {
  description = "Optional email endpoint for operational CloudWatch alarm notifications. AWS requires subscription confirmation before delivery begins."
  type        = string
  default     = null
  nullable    = true
}

variable "lambda_error_threshold" {
  description = "Number of Lambda invocation errors in a five-minute window that triggers an alarm."
  type        = number
  default     = 1

  validation {
    condition     = var.lambda_error_threshold >= 1
    error_message = "lambda_error_threshold must be at least 1."
  }
}

variable "lambda_duration_alarm_ms" {
  description = "P95 Lambda duration in milliseconds that triggers an alarm for two consecutive five-minute windows."
  type        = number
  default     = 8000

  validation {
    condition     = var.lambda_duration_alarm_ms > 0 && var.lambda_duration_alarm_ms < 10000
    error_message = "lambda_duration_alarm_ms must be greater than 0 and below the current 10-second Lambda timeout."
  }
}

variable "sqs_oldest_message_age_seconds" {
  description = "Maximum acceptable age of the oldest processed-events SQS message before an alarm triggers."
  type        = number
  default     = 120

  validation {
    condition     = var.sqs_oldest_message_age_seconds >= 60
    error_message = "sqs_oldest_message_age_seconds must be at least 60 seconds."
  }
}
