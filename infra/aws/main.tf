locals {
  processor_function_name     = "${var.name_prefix}-ride-event-processor"
  notification_function_name  = "${var.name_prefix}-notification-worker"
  effective_msk_cluster_arn   = var.msk_cluster_arn != null ? var.msk_cluster_arn : try(aws_msk_serverless_cluster.dev[0].arn, null)
  msk_topic_arn = local.effective_msk_cluster_arn == null ? null : "${replace(
    local.effective_msk_cluster_arn,
    ":cluster/",
    ":topic/"
  )}/${var.ride_events_topic}"
  msk_group_arn = local.effective_msk_cluster_arn == null ? null : "${replace(
    local.effective_msk_cluster_arn,
    ":cluster/",
    ":group/"
  )}/${var.consumer_group_id}"
}

data "archive_file" "ride_event_processor" {
  type        = "zip"
  source_dir  = "${path.module}/../../serverless/ride_event_processor"
  output_path = "${path.module}/build/ride_event_processor.zip"
}

data "archive_file" "notification_worker" {
  type        = "zip"
  source_dir  = "${path.module}/../../serverless/notification_worker"
  output_path = "${path.module}/build/notification_worker.zip"
}

resource "aws_sqs_queue" "processed_events_dlq" {
  name                      = "${var.name_prefix}-processed-events-dlq"
  message_retention_seconds = 1209600
}

resource "aws_sqs_queue" "processed_events" {
  name                       = "${var.name_prefix}-processed-events"
  message_retention_seconds  = 345600
  visibility_timeout_seconds = 60

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.processed_events_dlq.arn
    maxReceiveCount     = 5
  })
}

resource "aws_sns_topic" "ride_notifications" {
  name = "${var.name_prefix}-ride-notifications"
}

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ride_event_processor" {
  name               = "${local.processor_function_name}-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role" "notification_worker" {
  name               = "${local.notification_function_name}-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "processor_basic_logs" {
  role       = aws_iam_role.ride_event_processor.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "notification_basic_logs" {
  role       = aws_iam_role.notification_worker.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "aws_iam_policy_document" "processor_permissions" {
  statement {
    sid       = "SendProcessedEvents"
    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.processed_events.arn]
  }

  dynamic "statement" {
    for_each = local.effective_msk_cluster_arn == null ? [] : [local.effective_msk_cluster_arn]

    content {
      sid = "DiscoverMskCluster"
      actions = [
        "kafka:DescribeCluster",
        "kafka:DescribeClusterV2",
        "kafka:GetBootstrapBrokers",
      ]
      resources = [statement.value]
    }
  }

  dynamic "statement" {
    for_each = local.effective_msk_cluster_arn == null ? [] : [local.effective_msk_cluster_arn]

    content {
      sid       = "ConnectToMskCluster"
      actions   = ["kafka-cluster:Connect"]
      resources = [statement.value]
    }
  }

  dynamic "statement" {
    for_each = local.msk_topic_arn == null ? [] : [local.msk_topic_arn]

    content {
      sid = "ReadRideEventsTopic"
      actions = [
        "kafka-cluster:DescribeTopic",
        "kafka-cluster:ReadData",
      ]
      resources = [statement.value]
    }
  }

  dynamic "statement" {
    for_each = local.msk_group_arn == null ? [] : [local.msk_group_arn]

    content {
      sid = "UseMskConsumerGroup"
      actions = [
        "kafka-cluster:AlterGroup",
        "kafka-cluster:DescribeGroup",
      ]
      resources = [statement.value]
    }
  }

  dynamic "statement" {
    for_each = local.effective_msk_cluster_arn == null ? [] : [1]

    content {
      sid = "ManageMskNetworkInterfaces"
      actions = [
        "ec2:CreateNetworkInterface",
        "ec2:DeleteNetworkInterface",
        "ec2:DescribeNetworkInterfaces",
        "ec2:DescribeSecurityGroups",
        "ec2:DescribeSubnets",
        "ec2:DescribeVpcs",
      ]
      resources = ["*"]
    }
  }
}

resource "aws_iam_role_policy" "processor_permissions" {
  name   = "${local.processor_function_name}-permissions"
  role   = aws_iam_role.ride_event_processor.id
  policy = data.aws_iam_policy_document.processor_permissions.json
}

data "aws_iam_policy_document" "notification_permissions" {
  statement {
    sid = "ConsumeProcessedEvents"
    actions = [
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
      "sqs:ReceiveMessage",
    ]
    resources = [aws_sqs_queue.processed_events.arn]
  }

  statement {
    sid       = "PublishRideNotifications"
    actions   = ["sns:Publish"]
    resources = [aws_sns_topic.ride_notifications.arn]
  }
}

resource "aws_iam_role_policy" "notification_permissions" {
  name   = "${local.notification_function_name}-permissions"
  role   = aws_iam_role.notification_worker.id
  policy = data.aws_iam_policy_document.notification_permissions.json
}

resource "aws_cloudwatch_log_group" "ride_event_processor" {
  name              = "/aws/lambda/${local.processor_function_name}"
  retention_in_days = var.log_retention_days
}

resource "aws_cloudwatch_log_group" "notification_worker" {
  name              = "/aws/lambda/${local.notification_function_name}"
  retention_in_days = var.log_retention_days
}

resource "aws_lambda_function" "ride_event_processor" {
  function_name = local.processor_function_name
  description   = "Normalize Amazon MSK ride events and forward them to SQS."
  role          = aws_iam_role.ride_event_processor.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.11"
  memory_size   = var.lambda_memory_mb
  timeout       = 10

  filename         = data.archive_file.ride_event_processor.output_path
  source_code_hash = data.archive_file.ride_event_processor.output_base64sha256

  environment {
    variables = {
      PROCESSED_EVENTS_QUEUE_URL = aws_sqs_queue.processed_events.url
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.ride_event_processor,
    aws_iam_role_policy.processor_permissions,
    aws_iam_role_policy_attachment.processor_basic_logs,
  ]
}

resource "aws_lambda_function" "notification_worker" {
  function_name = local.notification_function_name
  description   = "Publish selected ride lifecycle events from SQS to SNS."
  role          = aws_iam_role.notification_worker.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.11"
  memory_size   = var.lambda_memory_mb
  timeout       = 10

  filename         = data.archive_file.notification_worker.output_path
  source_code_hash = data.archive_file.notification_worker.output_base64sha256

  environment {
    variables = {
      NOTIFICATION_TOPIC_ARN = aws_sns_topic.ride_notifications.arn
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.notification_worker,
    aws_iam_role_policy.notification_permissions,
    aws_iam_role_policy_attachment.notification_basic_logs,
  ]
}

resource "aws_lambda_event_source_mapping" "processed_events" {
  event_source_arn        = aws_sqs_queue.processed_events.arn
  function_name           = aws_lambda_function.notification_worker.arn
  batch_size              = 10
  enabled                 = true
  function_response_types = ["ReportBatchItemFailures"]
}

resource "aws_lambda_event_source_mapping" "ride_events_msk" {
  count = local.effective_msk_cluster_arn == null ? 0 : 1

  event_source_arn                   = local.effective_msk_cluster_arn
  function_name                      = aws_lambda_function.ride_event_processor.arn
  topics                             = [var.ride_events_topic]
  starting_position                  = "LATEST"
  batch_size                         = 100
  maximum_batching_window_in_seconds = 1

  amazon_managed_kafka_event_source_config {
    consumer_group_id = var.consumer_group_id
  }

  depends_on = [aws_iam_role_policy.processor_permissions]
}
