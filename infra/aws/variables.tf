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
