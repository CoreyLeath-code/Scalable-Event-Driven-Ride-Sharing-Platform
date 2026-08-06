"""Regenerate the benchmark, coverage, quality, and inventory artifacts cited in README."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_ARTIFACT = ROOT / "benchmark-results.json"
COVERAGE_ARTIFACT = ROOT / "coverage.xml"
REPRODUCIBILITY_ARTIFACT = ROOT / "reproducibility-results.json"
TYPE_CHECK_TARGETS = [
    "models.py",
    "utils.py",
    "event_bus.py",
    "location_store.py",
    "matching_engine.py",
    "pricing_engine.py",
    "consumer.py",
]


def run_command(name: str, command: list[str]) -> dict[str, object]:
    """Run one required validation command and retain its exact invocation."""
    completed = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    result = {
        "command": " ".join(command),
        "return_code": completed.returncode,
    }
    if completed.returncode != 0:
        sys.stdout.write(completed.stdout)
        sys.stderr.write(completed.stderr)
        raise RuntimeError(f"{name} failed with exit code {completed.returncode}")
    return result


def tracked_paths() -> list[str]:
    completed = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [path for path in completed.stdout.splitlines() if path]


def coverage_percent() -> float:
    root = ET.parse(COVERAGE_ARTIFACT).getroot()
    return round(float(root.attrib["line-rate"]) * 100, 2)


def main() -> None:
    results: dict[str, object] = {
        "schema_version": 1,
        "artifacts": {
            "benchmark": BENCHMARK_ARTIFACT.name,
            "coverage": COVERAGE_ARTIFACT.name,
            "reproducibility": REPRODUCIBILITY_ARTIFACT.name,
        },
        "commands": {},
    }
    commands = results["commands"]

    commands["format"] = run_command(
        "format check", [sys.executable, "-m", "black", "--check", ".", "--line-length=100"]
    )
    commands["lint"] = run_command("lint", [sys.executable, "-m", "ruff", "check", "."])
    commands["type_check"] = run_command(
        "type check",
        [sys.executable, "-m", "mypy", *TYPE_CHECK_TARGETS, "--ignore-missing-imports"],
    )
    commands["tests"] = run_command(
        "tests and coverage",
        [
            sys.executable,
            "-m",
            "pytest",
            "--cov=.",
            "--cov-report=term-missing",
            f"--cov-report=xml:{COVERAGE_ARTIFACT.name}",
        ],
    )
    commands["benchmark"] = run_command(
        "benchmark",
        [
            sys.executable,
            "benchmarks/ride_sharing_benchmarks.py",
            "--iterations",
            "500",
            "--driver-count",
            "100",
            "--output",
            BENCHMARK_ARTIFACT.name,
        ],
    )
    commands["benchmark_json"] = run_command(
        "benchmark JSON validation",
        [sys.executable, "-m", "json.tool", BENCHMARK_ARTIFACT.name],
    )

    paths = tracked_paths()
    benchmark = json.loads(BENCHMARK_ARTIFACT.read_text(encoding="utf-8"))
    results["engineering"] = {
        "tracked_repository_files": len(paths),
        "python_files": sum(path.endswith(".py") for path in paths),
        "test_files": sum(Path(path).name.startswith("test_") and path.endswith(".py") for path in paths),
        "github_actions_workflows": sum(path.startswith(".github/workflows/") for path in paths),
        "infrastructure_manifests": sum(
            path == "Dockerfile"
            or path == "docker-compose.yml"
            or path.startswith("infra/kubernetes/")
            for path in paths
        ),
    }
    results["coverage"] = {
        "line_coverage_percent": coverage_percent(),
        "report": COVERAGE_ARTIFACT.name,
    }
    results["benchmark"] = benchmark
    REPRODUCIBILITY_ARTIFACT.write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print(error, file=sys.stderr)
        raise SystemExit(1) from error
