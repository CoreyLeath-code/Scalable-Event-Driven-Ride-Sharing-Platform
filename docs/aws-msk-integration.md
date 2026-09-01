# Real Amazon MSK Development Integration Evidence

This repository includes a deliberately opt-in path for measuring the real AWS event chain:

```text
MSK Serverless -> Lambda ride-event processor -> SQS -> Lambda notification worker -> SNS -> probe SQS
```

The local/unit test suite does **not** require AWS credentials. Real-cloud evidence is produced only by the manual `Real AWS MSK Integration Evidence` workflow.

## Why the workflow requires a VPC-connected runner

The development MSK Serverless cluster is private and uses IAM authentication. The integration producer must therefore run from a network path that can reach the MSK VPC. The workflow targets a self-hosted runner labeled:

```text
self-hosted, linux, aws-msk-dev
```

This avoids making the Kafka brokers public merely so a GitHub-hosted runner can reach them.

## AWS resources

When `create_dev_msk_cluster=true`, Terraform can create:

- a private MSK Serverless cluster;
- an MSK security group;
- the existing Lambda event-source mapping using the created cluster ARN;
- an optional SNS-subscribed SQS probe queue when `enable_integration_probe=true`.

Both features are disabled by default because they create billable AWS resources.

## Authentication

The development cluster enables MSK IAM authentication. The Lambda execution role receives the scoped `kafka` and `kafka-cluster` permissions needed by the existing event-source mapping. The measurement runner uses the AWS MSK IAM SASL signer and short-lived AWS workload credentials.

AWS reference: https://docs.aws.amazon.com/lambda/latest/dg/msk-cluster-auth.html

## Manual workflow prerequisites

Create a GitHub `development` environment with:

- secret `AWS_MSK_INTEGRATION_ROLE_ARN`: IAM role trusted by GitHub OIDC and allowed to manage the development integration resources;
- a VPC-connected self-hosted runner carrying the `aws-msk-dev` label.

When dispatching the workflow, provide:

- AWS region;
- development VPC ID;
- a JSON array containing at least two private subnet IDs;
- probe sample count;
- whether the temporary stack should be destroyed after the run.

## Evidence artifact

`scripts/aws_msk_e2e.py` publishes synthetic `trip.completed` events containing only pseudonymous operational IDs. For each event it waits until the matching `probe_id` reaches the SNS-subscribed probe queue.

The generated JSON records:

- sample count;
- min/mean/p50/p95/p99/max end-to-end latency;
- cluster ARN, region, topic, and elapsed test time;
- an explicit request-count/runtime cost estimate based on pricing inputs supplied to the workflow.

The cost value is labeled an **estimate**, not AWS billing data. It intentionally does not claim to include every charge such as data transfer or CloudWatch ingestion. For billed-cost evidence, correlate the run with AWS Cost Explorer after billing data is available.

## Current evidence status

`evidence/aws-msk-integration-results.json` is checked in with `status: not_run`. That is intentional. No cloud latency or cost number should be copied into the README until an authorized real-AWS workflow run produces the evidence artifact and that artifact is reviewed/committed with its source commit and environment details.
