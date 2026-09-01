from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
K8S = ROOT / "infra" / "kubernetes"


def test_base_deployment_has_parameterized_image_and_rollout_safety():
    deployment = (K8S / "base" / "api-gateway-deployment.yaml").read_text(encoding="utf-8")
    assert "image: api-gateway:local" in deployment
    assert "revisionHistoryLimit: 10" in deployment
    assert "maxUnavailable: 0" in deployment
    assert "yourdockerhub" not in deployment
    assert ":latest" not in deployment


def test_environment_overlays_are_explicit_and_do_not_use_latest():
    expected_image = "newName: ghcr.io/coreyleath-code/scalable-event-driven-ride-sharing-platform"
    for environment in ("dev", "staging", "prod"):
        overlay_path = K8S / "overlays" / environment / "kustomization.yaml"
        overlay = overlay_path.read_text(encoding="utf-8")
        assert f"APP_ENV={environment}" in overlay
        assert expected_image in overlay
        assert ":latest" not in overlay


def test_staging_and_prod_require_authentication():
    for environment in ("staging", "prod"):
        overlay_path = K8S / "overlays" / environment / "kustomization.yaml"
        overlay = overlay_path.read_text(encoding="utf-8")
        assert "AUTH_REQUIRED=true" in overlay
