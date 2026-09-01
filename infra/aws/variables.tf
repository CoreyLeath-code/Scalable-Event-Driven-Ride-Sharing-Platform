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
  description = "Optional existing Amazon MSK cluster ARN. When null, Terraform can optionally create a development MSK Serverless cluster."
  type        = string
  default     = null
  nullable    = true
}

variable "create_dev_msk_cluster" {
  description = "Create a private IAM-authenticated MSK Serverless cluster for development integration measurements. Disabled by default because it incurs AWS cost."
  type        = bool
  default     = false
}

variable "dev_msk_vpc_id" {
  description = "VPC ID used by the optional development MSK Serverless cluster."
  type        = string
  default     = null
  nullable    = true

  validation {
    condition     = !var.create_dev_msk_cluster || var.dev_msk_vpc_id != null
    error_message = "dev_msk_vpc_id is required when create_dev_msk_cluster=true."
  }
}

variable "dev_msk_subnet_ids" {
  description = "Private subnet IDs used by the optional development MSK Serverless cluster."
  type        = list(string)
  default     = []

  validation {
    condition     = !var.create_dev_msk_cluster || length(var.dev_msk_subnet_ids) >= 2
    error_message = "At least two private subnet IDs are required when create_dev_msk_cluster=true."
  }
}

variable "enable_integration_probe" {
  description = "Create an SNS-subscribed SQS probe queue for real end-to-end MSK integration measurements."
  type        = bool
  default     = false
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

variable "create_runtime_secret" {
  description = "Create KMS-protected Secrets Manager secret metadata and a least-privilege reader policy. Secret values are never stored in Terraform."
  type        = bool
  default     = false
}

variable "runtime_secret_name" {
  description = "Optional Secrets Manager name for application runtime configuration."
  type        = string
  default     = null
  nullable    = true
}
