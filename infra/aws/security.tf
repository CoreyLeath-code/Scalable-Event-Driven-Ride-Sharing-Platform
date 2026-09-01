resource "aws_kms_key" "runtime_secrets" {
  count = var.create_runtime_secret ? 1 : 0

  description             = "KMS key for ride-sharing runtime secrets."
  enable_key_rotation     = true
  deletion_window_in_days = 7
}

resource "aws_kms_alias" "runtime_secrets" {
  count = var.create_runtime_secret ? 1 : 0

  name          = "alias/${var.name_prefix}-runtime-secrets"
  target_key_id = aws_kms_key.runtime_secrets[0].key_id
}

resource "aws_secretsmanager_secret" "runtime" {
  count = var.create_runtime_secret ? 1 : 0

  name                    = var.runtime_secret_name != null ? var.runtime_secret_name : "${var.name_prefix}/dev/runtime"
  description             = "Runtime configuration secret metadata. Populate values out-of-band; Terraform does not store secret material."
  kms_key_id              = aws_kms_key.runtime_secrets[0].arn
  recovery_window_in_days = 7
}

data "aws_iam_policy_document" "runtime_secret_reader" {
  count = var.create_runtime_secret ? 1 : 0

  statement {
    sid       = "ReadRuntimeSecret"
    actions   = ["secretsmanager:GetSecretValue"]
    resources = [aws_secretsmanager_secret.runtime[0].arn]
  }

  statement {
    sid       = "DecryptRuntimeSecret"
    actions   = ["kms:Decrypt"]
    resources = [aws_kms_key.runtime_secrets[0].arn]
  }
}

resource "aws_iam_policy" "runtime_secret_reader" {
  count = var.create_runtime_secret ? 1 : 0

  name   = "${var.name_prefix}-runtime-secret-reader"
  policy = data.aws_iam_policy_document.runtime_secret_reader[0].json
}
