locals {
  observability_namespace = "RideSharing/Serverless"
  dashboard_name          = "${var.name_prefix}-serverless-observability"
}

resource "aws_sns_topic" "operational_alerts" {
  name = "${var.name_prefix}-operational-alerts"
}

resource "aws_sns_topic_subscription" "operational_alert_email" {
  count = var.alarm_email == null ? 0 : 1

  topic_arn = aws_sns_topic.operational_alerts.arn
  protocol  = "email"
  endpoint  = var.alarm_email
}

resource "aws_cloudwatch_log_metric_filter" "notification_processing_failures" {
  name           = "${var.name_prefix}-notification-processing-failures"
  log_group_name = aws_cloudwatch_log_group.notification_worker.name
  pattern        = "\"Failed to process SQS notification record\""

  metric_transformation {
    name          = "NotificationProcessingFailures"
    namespace     = local.observability_namespace
    value         = "1"
    default_value = "0"
    unit          = "Count"
  }
}

resource "aws_cloudwatch_metric_alarm" "processor_errors" {
  alarm_name          = "${var.name_prefix}-ride-event-processor-errors"
  alarm_description   = "Ride-event processor Lambda reported one or more errors in the evaluation window."
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = var.lambda_error_threshold
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.ride_event_processor.function_name
  }

  alarm_actions = [aws_sns_topic.operational_alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "notification_errors" {
  alarm_name          = "${var.name_prefix}-notification-worker-errors"
  alarm_description   = "Notification worker Lambda reported one or more invocation errors in the evaluation window."
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = var.lambda_error_threshold
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.notification_worker.function_name
  }

  alarm_actions = [aws_sns_topic.operational_alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "processor_throttles" {
  alarm_name          = "${var.name_prefix}-ride-event-processor-throttles"
  alarm_description   = "Ride-event processor Lambda was throttled."
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "Throttles"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 1
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.ride_event_processor.function_name
  }

  alarm_actions = [aws_sns_topic.operational_alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "notification_throttles" {
  alarm_name          = "${var.name_prefix}-notification-worker-throttles"
  alarm_description   = "Notification worker Lambda was throttled."
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "Throttles"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 1
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.notification_worker.function_name
  }

  alarm_actions = [aws_sns_topic.operational_alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "processor_duration" {
  alarm_name          = "${var.name_prefix}-ride-event-processor-duration-p95"
  alarm_description   = "Ride-event processor p95 duration is approaching its configured timeout."
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = 300
  extended_statistic  = "p95"
  threshold           = var.lambda_duration_alarm_ms
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.ride_event_processor.function_name
  }

  alarm_actions = [aws_sns_topic.operational_alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "notification_duration" {
  alarm_name          = "${var.name_prefix}-notification-worker-duration-p95"
  alarm_description   = "Notification worker p95 duration is approaching its configured timeout."
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = 300
  extended_statistic  = "p95"
  threshold           = var.lambda_duration_alarm_ms
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.notification_worker.function_name
  }

  alarm_actions = [aws_sns_topic.operational_alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "processed_events_age" {
  alarm_name          = "${var.name_prefix}-processed-events-oldest-message"
  alarm_description   = "The processed-events queue contains an old message, indicating consumer lag or repeated processing delays."
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "ApproximateAgeOfOldestMessage"
  namespace           = "AWS/SQS"
  period              = 60
  statistic           = "Maximum"
  threshold           = var.sqs_oldest_message_age_seconds
  treat_missing_data  = "notBreaching"

  dimensions = {
    QueueName = aws_sqs_queue.processed_events.name
  }

  alarm_actions = [aws_sns_topic.operational_alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "processed_events_dlq" {
  alarm_name          = "${var.name_prefix}-processed-events-dlq-not-empty"
  alarm_description   = "At least one processed event reached the dead-letter queue and requires investigation."
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 60
  statistic           = "Maximum"
  threshold           = 1
  treat_missing_data  = "notBreaching"

  dimensions = {
    QueueName = aws_sqs_queue.processed_events_dlq.name
  }

  alarm_actions = [aws_sns_topic.operational_alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "notification_processing_failures" {
  alarm_name          = "${var.name_prefix}-notification-processing-failures"
  alarm_description   = "The notification worker logged one or more record-level processing failures."
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = aws_cloudwatch_log_metric_filter.notification_processing_failures.metric_transformation[0].name
  namespace           = local.observability_namespace
  period              = 300
  statistic           = "Sum"
  threshold           = 1
  treat_missing_data  = "notBreaching"

  alarm_actions = [aws_sns_topic.operational_alerts.arn]
}

resource "aws_cloudwatch_dashboard" "serverless" {
  dashboard_name = local.dashboard_name

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          title   = "Lambda invocations and errors"
          region  = var.aws_region
          view    = "timeSeries"
          stacked = false
          period  = 300
          stat    = "Sum"
          metrics = [
            ["AWS/Lambda", "Invocations", "FunctionName", local.processor_function_name, { label = "Processor invocations" }],
            ["AWS/Lambda", "Errors", "FunctionName", local.processor_function_name, { label = "Processor errors" }],
            ["AWS/Lambda", "Invocations", "FunctionName", local.notification_function_name, { label = "Notification invocations" }],
            ["AWS/Lambda", "Errors", "FunctionName", local.notification_function_name, { label = "Notification errors" }],
          ]
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "Lambda duration p95"
          region = var.aws_region
          view   = "timeSeries"
          period = 300
          stat   = "p95"
          metrics = [
            ["AWS/Lambda", "Duration", "FunctionName", local.processor_function_name, { label = "Processor duration" }],
            ["AWS/Lambda", "Duration", "FunctionName", local.notification_function_name, { label = "Notification duration" }],
          ]
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          title   = "Lambda throttles and concurrency"
          region  = var.aws_region
          view    = "timeSeries"
          stacked = false
          period  = 300
          metrics = [
            ["AWS/Lambda", "Throttles", "FunctionName", local.processor_function_name, { stat = "Sum", label = "Processor throttles" }],
            ["AWS/Lambda", "Throttles", "FunctionName", local.notification_function_name, { stat = "Sum", label = "Notification throttles" }],
            ["AWS/Lambda", "ConcurrentExecutions", "FunctionName", local.processor_function_name, { stat = "Maximum", label = "Processor concurrency", yAxis = "right" }],
            ["AWS/Lambda", "ConcurrentExecutions", "FunctionName", local.notification_function_name, { stat = "Maximum", label = "Notification concurrency", yAxis = "right" }],
          ]
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6
        properties = {
          title   = "SQS backlog and DLQ"
          region  = var.aws_region
          view    = "timeSeries"
          stacked = false
          period  = 60
          metrics = [
            ["AWS/SQS", "ApproximateNumberOfMessagesVisible", "QueueName", aws_sqs_queue.processed_events.name, { stat = "Maximum", label = "Processed-events visible" }],
            ["AWS/SQS", "ApproximateAgeOfOldestMessage", "QueueName", aws_sqs_queue.processed_events.name, { stat = "Maximum", label = "Oldest message age (s)", yAxis = "right" }],
            ["AWS/SQS", "ApproximateNumberOfMessagesVisible", "QueueName", aws_sqs_queue.processed_events_dlq.name, { stat = "Maximum", label = "DLQ visible" }],
          ]
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 12
        width  = 12
        height = 6
        properties = {
          title  = "Record-level notification failures"
          region = var.aws_region
          view   = "timeSeries"
          period = 300
          stat   = "Sum"
          metrics = [
            [local.observability_namespace, "NotificationProcessingFailures", { label = "Failed SQS records" }],
          ]
        }
      },
      {
        type   = "log"
        x      = 12
        y      = 12
        width  = 12
        height = 6
        properties = {
          title  = "Recent notification worker failures"
          region = var.aws_region
          view   = "table"
          query  = "SOURCE '${aws_cloudwatch_log_group.notification_worker.name}' | fields @timestamp, @message | filter @message like /Failed|ERROR|Exception/ | sort @timestamp desc | limit 50"
        }
      }
    ]
  })
}
