#!/usr/bin/env python3
"""Validate JDS-002 change records and validation campaigns."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        if path.suffix == ".json":
            return json.load(handle)
        return yaml.safe_load(handle)


def _schema_validator(path: Path) -> Draft202012Validator:
    schema = _load(path)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _iter_records(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(
        path
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in {".yaml", ".yml", ".json"}
    )


def _format_errors(
    validator: Draft202012Validator, document: Any, path: Path
) -> list[str]:
    errors = []
    for error in sorted(validator.iter_errors(document), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.path) or "<root>"
        errors.append(f"{path}:{location}: {error.message}")
    return errors


def _change_semantics(document: dict[str, Any], path: Path) -> list[str]:
    errors: list[str] = []
    state = document["state"]
    disposition = document["disposition"]
    classification = document["classification"]
    version_effect = document["versionEffect"]
    validation = document["validation"]

    if disposition == "DEFER" and state in {"PROMOTED", "LIVE_VERIFIED"}:
        errors.append(f"{path}: deferred change cannot be {state}")
    if disposition == "REJECT" and state not in {"REJECTED", "CLOSED", "SUPERSEDED"}:
        errors.append(
            f"{path}: rejected disposition requires REJECTED/CLOSED/SUPERSEDED state"
        )
    if classification == "DOC_ONLY" and version_effect != "NONE":
        errors.append(f"{path}: DOC_ONLY requires versionEffect NONE")
    if classification == "BREAKING_CHANGE" and version_effect != "MAJOR":
        errors.append(f"{path}: BREAKING_CHANGE requires versionEffect MAJOR")

    if state in {"ACCEPTED", "PROMOTED", "LIVE_VERIFIED", "CLOSED"}:
        for gate in ("targeted", "regression", "security"):
            if validation[gate] == "FAIL":
                errors.append(
                    f"{path}: {state} change cannot retain validation.{gate}=FAIL"
                )

    if state in {"PROMOTED", "LIVE_VERIFIED"}:
        promotion = document.get("promotion") or {}
        if not (promotion.get("commit") or promotion.get("artifactDigest")):
            errors.append(f"{path}: {state} requires promotion commit or artifactDigest")
        if not document.get("targetRelease"):
            errors.append(f"{path}: {state} requires targetRelease")

    if state == "LIVE_VERIFIED" and validation["runtime"] != "PASS":
        errors.append(f"{path}: LIVE_VERIFIED requires validation.runtime=PASS")

    if disposition == "DEFER" and not document.get("deferredTo"):
        errors.append(f"{path}: DEFER requires deferredTo")

    return errors


def _campaign_semantics(document: dict[str, Any], path: Path) -> list[str]:
    errors: list[str] = []
    observations = document["observations"]
    state = document["state"]
    recommendation = document["promotionRecommendation"]

    ids = [item["id"] for item in observations]
    if len(ids) != len(set(ids)):
        errors.append(f"{path}: observation IDs must be unique")

    open_required_failures = [
        item["id"]
        for item in observations
        if item["required"]
        and item["result"] in {"FAIL", "BLOCKED"}
        and item["status"] == "OPEN"
    ]
    if state in {"PASSED", "CLOSED"} and open_required_failures:
        errors.append(
            f"{path}: {state} campaign has open required failures: "
            + ", ".join(open_required_failures)
        )
    if recommendation == "ACCEPT" and open_required_failures:
        errors.append(f"{path}: ACCEPT recommendation cannot have open required failures")
    if state == "PASSED" and recommendation != "ACCEPT":
        errors.append(f"{path}: PASSED campaign requires promotionRecommendation ACCEPT")

    for observation in observations:
        if (
            observation["required"]
            and observation["result"] in {"FAIL", "BLOCKED"}
            and observation["status"] == "RESOLVED"
            and not observation.get("changeRecord")
        ):
            errors.append(
                f"{path}: resolved required failure {observation['id']} "
                "must link a changeRecord"
            )
    return errors


def validate(
    *,
    change_dir: Path,
    campaign_dir: Path,
    change_schema: Path,
    campaign_schema: Path,
) -> list[str]:
    errors: list[str] = []
    change_validator = _schema_validator(change_schema)
    campaign_validator = _schema_validator(campaign_schema)

    for path in _iter_records(change_dir):
        document = _load(path)
        format_errors = _format_errors(change_validator, document, path)
        errors.extend(format_errors)
        if isinstance(document, dict) and not format_errors:
            errors.extend(_change_semantics(document, path))

    for path in _iter_records(campaign_dir):
        document = _load(path)
        format_errors = _format_errors(campaign_validator, document, path)
        errors.extend(format_errors)
        if isinstance(document, dict) and not format_errors:
            errors.extend(_campaign_semantics(document, path))

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--change-dir", type=Path, default=Path("changes"))
    parser.add_argument("--campaign-dir", type=Path, default=Path("validation"))
    parser.add_argument(
        "--change-schema",
        type=Path,
        default=Path("schemas/change-record.schema.json"),
    )
    parser.add_argument(
        "--campaign-schema",
        type=Path,
        default=Path("schemas/validation-campaign.schema.json"),
    )
    args = parser.parse_args()

    errors = validate(
        change_dir=args.change_dir,
        campaign_dir=args.campaign_dir,
        change_schema=args.change_schema,
        campaign_schema=args.campaign_schema,
    )
    if errors:
        for error in errors:
            print(error)
        print(f"JDS002_RELEASE_GOVERNANCE_FAIL errors={len(errors)}")
        return 1

    change_count = len(_iter_records(args.change_dir))
    campaign_count = len(_iter_records(args.campaign_dir))
    print(
        "JDS002_RELEASE_GOVERNANCE_OK "
        f"changes={change_count} campaigns={campaign_count}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
