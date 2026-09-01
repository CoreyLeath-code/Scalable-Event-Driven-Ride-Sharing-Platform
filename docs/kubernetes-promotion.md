# Kubernetes Environment Promotion and Rollback Evidence

The Kubernetes manifests use a Kustomize base with explicit `dev`, `staging`, and `prod` overlays.

## Layout

```text
infra/kubernetes/
|-- api-gateway-deployment.yaml
|-- api-gateway-hpa.yaml
|-- kustomization.yaml
`-- overlays/
    |-- dev/kustomization.yaml
    |-- staging/kustomization.yaml
    `-- prod/kustomization.yaml
```

The base deployment uses the logical image name `api-gateway:local`. Each overlay supplies the registry/repository and an environment placeholder tag. Promotion workflows replace that image in the ephemeral workflow workspace; repository manifests do not use `latest`.

## Environment boundaries

- `dev`: authentication disabled by default for controlled development.
- `staging`: authentication required; issuer/audience placeholders must be replaced before a real apply.
- `prod`: authentication required and deployment evidence requires an immutable `@sha256:` image digest.

Each overlay also sets a non-secret Secrets Manager identifier such as `ride-sharing/prod/runtime`. Workload credentials—not static AWS access keys—should authorize the pod to read that secret.

## Promotion workflow

`Kubernetes Promotion Evidence` supports two modes:

1. render-only (default): build the chosen overlay, validate it client-side, and upload the rendered manifest plus evidence JSON;
2. apply: load environment-scoped `KUBE_CONFIG_DATA`, capture the current deployment revision, apply the rendered manifest, wait for rollout success, then record before/after revisions.

The evidence JSON records:

- source Git commit;
- environment;
- image reference;
- whether the manifest was only rendered or actually applied;
- SHA-256 of the rendered manifest;
- before/after deployment revisions when available.

## Rollback workflow

`Kubernetes Rollback Evidence` requires an explicit revision. It captures the current revision, executes `kubectl rollout undo --to-revision`, waits for rollout success, snapshots the resulting Deployment YAML, and uploads a rollback evidence artifact.

## GitHub environment secret

For actual cluster changes, configure `KUBE_CONFIG_DATA` as a base64-encoded kubeconfig in each GitHub Environment (`dev`, `staging`, `prod`). In a stronger production setup, replace static kubeconfig material with short-lived cloud workload identity and environment protection rules.

## Current evidence status

`evidence/kubernetes-deployment-results.json` says `not_run` until a promotion or rollback workflow is explicitly executed. Rendered manifests and workflow success are reproducible evidence; a real deployment/rollback claim requires the corresponding uploaded workflow artifact.
