resource "aws_security_group" "dev_msk" {
  count = var.create_dev_msk_cluster ? 1 : 0

  name_prefix = "${var.name_prefix}-dev-msk-"
  description = "Private security group for the optional development MSK Serverless cluster."
  vpc_id      = var.dev_msk_vpc_id

  ingress {
    description = "IAM-authenticated Kafka traffic within the cluster security group"
    from_port   = 9098
    to_port     = 9098
    protocol    = "tcp"
    self        = true
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_msk_serverless_cluster" "dev" {
  count = var.create_dev_msk_cluster ? 1 : 0

  cluster_name = "${var.name_prefix}-dev"

  vpc_config {
    subnet_ids         = var.dev_msk_subnet_ids
    security_group_ids = [aws_security_group.dev_msk[0].id]
  }

  client_authentication {
    sasl {
      iam {
        enabled = true
      }
    }
  }
}

resource "aws_sqs_queue" "integration_probe" {
  count = var.enable_integration_probe ? 1 : 0

  name                      = "${var.name_prefix}-integration-probe"
  message_retention_seconds = 3600
}

data "aws_iam_policy_document" "integration_probe" {
  count = var.enable_integration_probe ? 1 : 0

  statement {
    sid     = "AllowRideNotificationTopic"
    actions = ["sqs:SendMessage"]
    resources = [
      aws_sqs_queue.integration_probe[0].arn,
    ]

    principals {
      type        = "Service"
      identifiers = ["sns.amazonaws.com"]
    }

    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values   = [aws_sns_topic.ride_notifications.arn]
    }
  }
}

resource "aws_sqs_queue_policy" "integration_probe" {
  count = var.enable_integration_probe ? 1 : 0

  queue_url = aws_sqs_queue.integration_probe[0].url
  policy    = data.aws_iam_policy_document.integration_probe[0].json
}

resource "aws_sns_topic_subscription" "integration_probe" {
  count = var.enable_integration_probe ? 1 : 0

  topic_arn = aws_sns_topic.ride_notifications.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.integration_probe[0].arn

  depends_on = [aws_sqs_queue_policy.integration_probe]
}
