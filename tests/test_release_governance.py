from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_release_governance.py"

spec = importlib.util.spec_from_file_location("release_governance", SCRIPT)
assert spec and spec.loader
release_governance = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release_governance)


def _validate(change_dir: Path, campaign_dir: Path) -> list[str]:
    return release_governance.validate(
        change_dir=change_dir,
        campaign_dir=campaign_dir,
        change_schema=ROOT / "schemas" / "change-record.schema.json",
        campaign_schema=ROOT / "schemas" / "validation-campaign.schema.json",
    )


def test_canonical_examples_are_valid() -> None:
    errors = _validate(
        ROOT / "examples" / "release-governance" / "changes",
        ROOT / "examples" / "release-governance" / "validation",
    )
    assert errors == []


def test_passed_campaign_refuses_open_required_failure(tmp_path: Path) -> None:
    change_dir = tmp_path / "changes"
    campaign_dir = tmp_path / "validation"
    change_dir.mkdir()
    campaign_dir.mkdir()

    source = yaml.safe_load(
        (
            ROOT
            / "examples"
            / "release-governance"
            / "validation"
            / "VAL-BRIDGE-2-0-GA.yaml"
        ).read_text(encoding="utf-8")
    )
    source["state"] = "PASSED"
    source["promotionRecommendation"] = "ACCEPT"
    source["observations"][1]["status"] = "OPEN"
    (campaign_dir / "VAL-BRIDGE-2-0-GA.yaml").write_text(
        yaml.safe_dump(source, sort_keys=False),
        encoding="utf-8",
    )

    errors = _validate(change_dir, campaign_dir)
    assert any("open required failures" in error for error in errors)


def test_doc_only_cannot_increment_product_version(tmp_path: Path) -> None:
    change_dir = tmp_path / "changes"
    campaign_dir = tmp_path / "validation"
    change_dir.mkdir()
    campaign_dir.mkdir()

    source = yaml.safe_load(
        (
            ROOT
            / "examples"
            / "release-governance"
            / "changes"
            / "CHG-BRIDGE-001.yaml"
        ).read_text(encoding="utf-8")
    )
    source["classification"] = "DOC_ONLY"
    source["versionEffect"] = "PATCH"
    (change_dir / "CHG-DOC-001.yaml").write_text(
        yaml.safe_dump(source, sort_keys=False),
        encoding="utf-8",
    )

    errors = _validate(change_dir, campaign_dir)
    assert any("DOC_ONLY requires versionEffect NONE" in error for error in errors)


def test_live_verified_requires_runtime_pass_and_promotion_identity(tmp_path: Path) -> None:
    change_dir = tmp_path / "changes"
    campaign_dir = tmp_path / "validation"
    change_dir.mkdir()
    campaign_dir.mkdir()

    source = yaml.safe_load(
        (
            ROOT
            / "examples"
            / "release-governance"
            / "changes"
            / "CHG-BRIDGE-001.yaml"
        ).read_text(encoding="utf-8")
    )
    source["state"] = "LIVE_VERIFIED"
    source["validation"]["runtime"] = "NOT_RUN"
    source["promotion"]["commit"] = None
    source["promotion"]["artifactDigest"] = None
    (change_dir / "CHG-BRIDGE-001.yaml").write_text(
        yaml.safe_dump(source, sort_keys=False),
        encoding="utf-8",
    )

    errors = _validate(change_dir, campaign_dir)
    assert any("requires promotion commit or artifactDigest" in error for error in errors)
    assert any("LIVE_VERIFIED requires validation.runtime=PASS" in error for error in errors)
