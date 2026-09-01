# Authentication, Secrets, and PII Boundaries

This repository implements explicit security boundaries while keeping local development and unit tests credential-free.

## API authentication boundary

Sensitive driver-location collection endpoints use the FastAPI `require_authenticated_request` dependency:

- `/driver-location/drivers`
- `/driver-location/drivers/{driver_id}`
- `/driver-location/count`

Liveness and readiness remain unauthenticated so Kubernetes and load balancers can probe the service:

- `/driver-location/health`
- `/driver-location/ready`

Authentication is disabled by default for local development. Set `AUTH_REQUIRED=true` to enforce RS256 OIDC JWT verification.

Required production/staging configuration:

```text
AUTH_REQUIRED=true
AUTH_ISSUER=https://<issuer>
AUTH_AUDIENCE=<client-or-resource-audience>
AUTH_TOKEN_USE=access
```

`AUTH_JWKS_URL` may override the default `<issuer>/.well-known/jwks.json` location. The verifier accepts an OIDC `aud` claim or Cognito-style `client_id` audience and verifies the configured issuer.

Authentication is not the same as a complete authorization model. A production system still needs scopes/roles, object-level access checks, tenant boundaries, and policy ownership.

## Runtime secrets

`runtime_secrets.py` resolves the driver Redis connection in this order:

1. `DRIVER_LOCATION_REDIS_SECRET_ID` -> AWS Secrets Manager JSON field `redis_url`;
2. local-development fallback `DRIVER_LOCATION_REDIS_URL`.

The application does not log the secret value or raw Secrets Manager response.

Terraform can optionally create:

- a customer-managed KMS key with rotation enabled;
- Secrets Manager secret **metadata**;
- a least-privilege IAM policy containing `secretsmanager:GetSecretValue` and `kms:Decrypt` for only that secret/key.

Terraform intentionally does **not** create a `secret_version`; secret material is populated out-of-band so it is not written into Terraform configuration or state by this reference implementation.

Example secret JSON:

```json
{
  "redis_url": "redis://private-host:6379/0"
}
```

AWS recommends Secrets Manager instead of Lambda/application environment variables for credentials and sensitive authorization material.

## Direct PII policy

The asynchronous event path rejects fields whose names represent direct identifiers, including:

- email addresses;
- phone numbers;
- first/full/last names;
- home/street addresses;
- SSNs;
- payment card, bank account, routing, or CVV fields.

The Lambda MSK processor rejects such payloads before forwarding them to SQS. The notification worker applies the same check before SNS publication, so direct injection into the queue cannot bypass the boundary.

Pseudonymous operational identifiers such as `ride_id`, `driver_id`, and `probe_id` are permitted by this narrow guard. They can still be personal data in a real system and require retention/access policies appropriate to the deployment.

## Logging boundary

The in-memory event bus no longer logs message bodies. The driver telemetry consumer no longer logs coordinates or validation exception details that may echo input values. Operational logs contain topic names, record counts, message IDs, and pseudonymous IDs rather than raw rider/driver payloads.

## Production-claim rule

These controls demonstrate implemented boundaries; they are not a certification or proof of regulatory compliance. A production claim still requires threat modeling, authorization design, key/secret rotation procedures, retention/deletion policy, audit logging, access reviews, incident response, and verification against the actual deployment environment.
