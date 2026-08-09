from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
PLANNER = ROOT / ".github" / "actions" / "plan" / "planner.py"
CATALOG = ROOT / "catalog" / "capabilities.yml"

spec = importlib.util.spec_from_file_location("jep_planner", PLANNER)
assert spec and spec.loader
planner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(planner)


def manifest(
    *,
    preset: str = "containerized-python",
    criticality: str = "medium",
    add: list[str] | None = None,
    remove: list[str] | None = None,
    detection: bool = False,
) -> dict[str, Any]:
    return {
        "apiVersion": "engineering.jarvas/v1",
        "kind": "ProjectEngineeringProfile",
        "metadata": {"name": "test-project"},
        "spec": {
            "standard": "JDS-1.0",
            "platformRef": "v0.1.0",
            "criticality": criticality,
            "detection": {"enabled": detection},
            "preset": {"name": preset},
            "capabilities": {"add": add or [], "remove": remove or []},
            "delivery": {
                "releaseStrategy": "versioned",
                "liveAcceptance": "conditional",
                "requireEvidenceManifest": True,
            },
            "execution": {"strategy": "unspecified"},
            "overrides": {},
        },
    }


def catalogue() -> dict[str, Any]:
    payload = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_docs_only_skips_expensive_container_path() -> None:
    plan = planner.build_plan(
        manifest(),
        catalogue(),
        ["Dockerfile", "src/app.py", "docs/readme.md"],
        ["docs/readme.md"],
        "explicit",
    )
    assert plan["docsOnly"] is True
    assert plan["ambiguousImpact"] is False
    assert "docs" in plan["selectedGates"]
    assert "secret_scan" in plan["selectedGates"]
    assert "evidence" in plan["selectedGates"]
    assert "container_build" not in plan["selectedGates"]
    assert "container_scan" not in plan["selectedGates"]
    assert "isolated_acceptance" not in plan["selectedGates"]


def test_dockerfile_change_selects_image_assurance_chain() -> None:
    plan = planner.build_plan(
        manifest(),
        catalogue(),
        ["Dockerfile", "src/app.py"],
        ["Dockerfile"],
        "explicit",
    )
    assert plan["ambiguousImpact"] is False
    for gate in ("container_build", "container_scan", "sbom", "isolated_acceptance"):
        assert gate in plan["selectedGates"]
    assert "python_test" not in plan["selectedGates"]


def test_unknown_change_fails_safe_to_all_effective_capabilities() -> None:
    plan = planner.build_plan(
        manifest(),
        catalogue(),
        ["Dockerfile", "src/app.py"],
        ["assets/opaque.binary"],
        "explicit",
    )
    assert plan["ambiguousImpact"] is True
    assert set(plan["selectedCapabilities"]) == set(plan["effectiveCapabilities"])
    assert "python_test" in plan["selectedGates"]
    assert "container_build" in plan["selectedGates"]


def test_mandatory_secret_scan_cannot_be_removed() -> None:
    plan = planner.build_plan(
        manifest(remove=["security.secret-scan"]),
        catalogue(),
        ["docs/readme.md"],
        ["docs/readme.md"],
        "explicit",
    )
    assert "security.secret-scan" in plan["effectiveCapabilities"]
    assert "security.secret-scan" in plan["selectedCapabilities"]
    assert "remove-denied-by-policy" in plan["capabilityReasons"]["security.secret-scan"]


def test_high_criticality_forces_sca_even_without_preset_request() -> None:
    plan = planner.build_plan(
        manifest(preset="python-service", criticality="high", remove=["security.sca"]),
        catalogue(),
        ["src/app.py", "pyproject.toml"],
        ["src/app.py"],
        "explicit",
    )
    assert "security.sca" in plan["effectiveCapabilities"]
    assert "security.sca" in plan["selectedCapabilities"]
    assert "remove-denied-by-policy" in plan["capabilityReasons"]["security.sca"]


def test_dependency_closure_adds_container_build_for_container_scan() -> None:
    plan = planner.build_plan(
        manifest(preset="python-service", add=["security.container-scan"]),
        catalogue(),
        ["Dockerfile", "src/app.py"],
        ["Dockerfile"],
        "explicit",
    )
    assert "security.container-scan" in plan["selectedCapabilities"]
    assert "container.build" in plan["selectedCapabilities"]
    assert "container_build" in plan["selectedGates"]
