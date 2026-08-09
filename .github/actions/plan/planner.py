from __future__ import annotations

import argparse
import fnmatch
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Iterable

import jsonschema
import yaml

CRITICALITY_RANK = {"low": 0, "medium": 1, "high": 2, "critical": 3}
GROUP_PREFIXES = {
    "run-docs": ("docs",),
    "run-python": ("python_",),
    "run-security": ("secret_", "sca", "sast", "container_scan", "sbom", "host_safety"),
    "run-package": ("package",),
    "run-container": ("container_", "isolated_acceptance"),
    "run-browser": ("browser_",),
    "run-lab": ("lab_", "host_safety"),
    "run-evidence": ("evidence",),
}
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", ".mypy_cache", ".pytest_cache", "dist", "build"}


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a YAML object")
    return payload


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def matches(path: str, patterns: Iterable[str]) -> bool:
    normalized = path.replace("\\", "/").lstrip("./")
    return any(fnmatch.fnmatch(normalized, pattern) for pattern in patterns)


def repository_files(root: Path) -> list[str]:
    files: list[str] = []
    for current, dirs, names in os.walk(root):
        dirs[:] = [name for name in dirs if name not in SKIP_DIRS]
        current_path = Path(current)
        for name in names:
            path = (current_path / name).relative_to(root).as_posix()
            files.append(path)
    return sorted(files)


def git_changed_files(root: Path, base_ref: str | None) -> tuple[list[str], str]:
    candidates: list[list[str]] = []
    if base_ref:
        candidates.append(["git", "diff", "--name-only", f"{base_ref}...HEAD"])
        candidates.append(["git", "diff", "--name-only", base_ref, "HEAD"])
    else:
        candidates.append(["git", "diff", "--name-only", "HEAD^"])

    for command in candidates:
        result = subprocess.run(command, cwd=root, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            changed = sorted({line.strip() for line in result.stdout.splitlines() if line.strip()})
            return changed, "git-diff"
    return [], "unavailable"


def docs_only(paths: list[str]) -> bool:
    if not paths:
        return False
    for path in paths:
        normalized = path.replace("\\", "/")
        if normalized.endswith((".md", ".mdx", ".rst")):
            continue
        if normalized.startswith("docs/"):
            continue
        return False
    return True


def dependency_closure(selected: set[str], capabilities: dict[str, Any]) -> set[str]:
    resolved = set(selected)
    changed = True
    while changed:
        changed = False
        for capability_id in tuple(resolved):
            descriptor = capabilities[capability_id]
            for dependency in descriptor.get("dependsOn", []):
                if dependency not in capabilities:
                    raise ValueError(f"capability {capability_id} depends on unknown capability {dependency}")
                if dependency not in resolved:
                    resolved.add(dependency)
                    changed = True
    return resolved


def validate_catalog(catalog: dict[str, Any]) -> None:
    capabilities = catalog.get("capabilities")
    presets = catalog.get("presets")
    if not isinstance(capabilities, dict) or not capabilities:
        raise ValueError("catalog.capabilities must be a non-empty object")
    if not isinstance(presets, dict):
        raise ValueError("catalog.presets must be an object")

    for capability_id, descriptor in capabilities.items():
        if not isinstance(descriptor, dict):
            raise ValueError(f"capability {capability_id} must be an object")
        gates = descriptor.get("gates")
        triggers = descriptor.get("triggers")
        if not isinstance(gates, list) or not gates or not all(isinstance(value, str) for value in gates):
            raise ValueError(f"capability {capability_id} requires non-empty gates")
        if not isinstance(triggers, list) or not triggers or not all(isinstance(value, str) for value in triggers):
            raise ValueError(f"capability {capability_id} requires non-empty triggers")
        minimum = descriptor.get("minimumCriticality")
        if minimum is not None and minimum not in CRITICALITY_RANK:
            raise ValueError(f"capability {capability_id} has invalid minimumCriticality")

    for preset_name, preset in presets.items():
        if not isinstance(preset, dict) or not isinstance(preset.get("capabilities"), list):
            raise ValueError(f"preset {preset_name} must contain capabilities")
        unknown = sorted(set(preset["capabilities"]) - set(capabilities))
        if unknown:
            raise ValueError(f"preset {preset_name} references unknown capabilities: {unknown}")


def build_plan(
    manifest: dict[str, Any],
    catalog: dict[str, Any],
    repo_files: list[str],
    changed_files: list[str],
    change_source: str,
) -> dict[str, Any]:
    validate_catalog(catalog)
    spec = manifest["spec"]
    capabilities: dict[str, Any] = catalog["capabilities"]
    presets: dict[str, Any] = catalog["presets"]
    criticality = spec["criticality"]
    rank = CRITICALITY_RANK[criticality]

    effective: set[str] = set()
    reasons: dict[str, list[str]] = {}

    def add(capability_id: str, reason: str) -> None:
        if capability_id not in capabilities:
            raise ValueError(f"unknown capability: {capability_id}")
        effective.add(capability_id)
        reasons.setdefault(capability_id, []).append(reason)

    for capability_id, descriptor in capabilities.items():
        if descriptor.get("mandatory") is True:
            add(capability_id, "mandatory-policy")
        minimum = descriptor.get("minimumCriticality")
        if minimum is not None and rank >= CRITICALITY_RANK[minimum]:
            add(capability_id, f"criticality>={minimum}")

    preset = spec.get("preset")
    if preset:
        preset_name = preset["name"]
        if preset_name not in presets:
            raise ValueError(f"unknown preset: {preset_name}")
        for capability_id in presets[preset_name]["capabilities"]:
            add(capability_id, f"preset:{preset_name}")

    config = spec["capabilities"]
    for capability_id in config.get("add", []):
        add(capability_id, "explicit-add")

    detection_enabled = spec.get("detection", {}).get("enabled", True)
    if detection_enabled:
        for capability_id, descriptor in capabilities.items():
            if capability_id in effective:
                continue
            if any(matches(path, descriptor["triggers"]) for path in repo_files):
                add(capability_id, "auto-detected")

    requested_remove = set(config.get("remove", []))
    for capability_id in requested_remove:
        if capability_id not in capabilities:
            raise ValueError(f"cannot remove unknown capability: {capability_id}")
        descriptor = capabilities[capability_id]
        minimum = descriptor.get("minimumCriticality")
        mandatory_for_risk = minimum is not None and rank >= CRITICALITY_RANK[minimum]
        if descriptor.get("mandatory") is True or mandatory_for_risk:
            reasons.setdefault(capability_id, []).append("remove-denied-by-policy")
            effective.add(capability_id)
        else:
            effective.discard(capability_id)
            reasons.setdefault(capability_id, []).append("explicit-remove")

    effective = dependency_closure(effective, capabilities)
    for capability_id in effective:
        reasons.setdefault(capability_id, []).append("dependency-closure" if capability_id not in reasons else "effective")

    is_docs_only = docs_only(changed_files)
    per_capability_match = {
        capability_id: any(matches(path, capabilities[capability_id]["triggers"]) for path in changed_files)
        for capability_id in effective
    }
    any_nonmandatory_match = any(
        matched and not capabilities[capability_id].get("mandatory", False)
        for capability_id, matched in per_capability_match.items()
    )
    ambiguous = change_source == "unavailable" or (bool(changed_files) and not is_docs_only and not any_nonmandatory_match)

    selected: set[str] = set()
    skipped: dict[str, str] = {}
    for capability_id in sorted(effective):
        descriptor = capabilities[capability_id]
        minimum = descriptor.get("minimumCriticality")
        mandatory_for_risk = minimum is not None and rank >= CRITICALITY_RANK[minimum]
        mandatory = descriptor.get("mandatory") is True or mandatory_for_risk

        if mandatory:
            selected.add(capability_id)
        elif ambiguous or not changed_files:
            selected.add(capability_id)
        elif per_capability_match[capability_id]:
            selected.add(capability_id)
        elif is_docs_only and descriptor.get("skipOnDocsOnly") is False:
            selected.add(capability_id)
        else:
            skipped[capability_id] = "change-impact-not-triggered"

    selected = dependency_closure(selected, capabilities)
    selected_gates = sorted({gate for capability_id in selected for gate in capabilities[capability_id]["gates"]})

    plan: dict[str, Any] = {
        "schema": "engineering.jarvas/gate-plan-v1",
        "standard": spec["standard"],
        "platformRef": spec["platformRef"],
        "criticality": criticality,
        "changeSource": change_source,
        "changedFiles": changed_files,
        "docsOnly": is_docs_only,
        "ambiguousImpact": ambiguous,
        "effectiveCapabilities": sorted(effective),
        "selectedCapabilities": sorted(selected),
        "selectedGates": selected_gates,
        "skippedCapabilities": skipped,
        "capabilityReasons": {key: sorted(set(value)) for key, value in sorted(reasons.items())},
    }
    return plan


def group_output(gates: list[str], prefixes: tuple[str, ...]) -> str:
    return "true" if any(any(gate == prefix or gate.startswith(prefix) for prefix in prefixes) for gate in gates) else "false"


def emit_github_output(path: Path, plan: dict[str, Any]) -> None:
    compact = json.dumps(plan, separators=(",", ":"), sort_keys=True)
    gates = plan["selectedGates"]
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"plan-json={compact}\n")
        handle.write(f"selected-gates={','.join(gates)}\n")
        for output_name, prefixes in GROUP_PREFIXES.items():
            handle.write(f"{output_name}={group_output(gates, prefixes)}\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--base-ref")
    parser.add_argument("--changed-file", action="append", default=[])
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--github-output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = load_yaml(args.manifest)
    catalog = load_yaml(args.catalog)
    schema = load_json(args.schema)
    jsonschema.validate(manifest, schema)

    root = args.repo_root.resolve()
    repo_file_list = repository_files(root)
    if args.changed_file:
        changed_files = sorted(set(args.changed_file))
        change_source = "explicit"
    else:
        changed_files, change_source = git_changed_files(root, args.base_ref)

    plan = build_plan(manifest, catalog, repo_file_list, changed_files, change_source)
    rendered = json.dumps(plan, indent=2, sort_keys=True)
    print(rendered)
    if args.json_out:
        args.json_out.write_text(rendered + "\n", encoding="utf-8")
    if args.github_output:
        emit_github_output(args.github_output, plan)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
