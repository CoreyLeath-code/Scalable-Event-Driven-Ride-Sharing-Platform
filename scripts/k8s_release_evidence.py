"""Create deterministic Kubernetes promotion or rollback evidence JSON."""

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def manifest_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_evidence(
    *,
    action: str,
    environment: str,
    image: str,
    git_sha: str,
    manifest: Path,
    deployment_status: str,
    from_revision: str | None = None,
    to_revision: str | None = None,
) -> dict[str, object]:
    if action not in {"promote", "rollback"}:
        raise ValueError("action must be promote or rollback")
    if environment not in {"dev", "staging", "prod"}:
        raise ValueError("environment must be dev, staging, or prod")
    if deployment_status not in {"rendered", "applied"}:
        raise ValueError("deployment_status must be rendered or applied")
    if environment == "prod" and "@sha256:" not in image:
        raise ValueError("production promotion requires an immutable image digest")

    return {
        "schema_version": 1,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "environment": environment,
        "deployment_status": deployment_status,
        "image": image,
        "git_sha": git_sha,
        "manifest_sha256": manifest_sha256(manifest),
        "from_revision": from_revision,
        "to_revision": to_revision,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=["promote", "rollback"], required=True)
    parser.add_argument("--environment", choices=["dev", "staging", "prod"], required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--git-sha", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--deployment-status", choices=["rendered", "applied"], required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--from-revision")
    parser.add_argument("--to-revision")
    args = parser.parse_args()

    evidence = build_evidence(
        action=args.action,
        environment=args.environment,
        image=args.image,
        git_sha=args.git_sha,
        manifest=args.manifest,
        deployment_status=args.deployment_status,
        from_revision=args.from_revision,
        to_revision=args.to_revision,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
