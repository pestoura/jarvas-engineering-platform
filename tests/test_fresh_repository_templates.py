from pathlib import Path


PLATFORM_SHA = "9ee1147ea85bbb5bbb733d252bab9ccbb113f5ef"
ROOT = Path(__file__).resolve().parents[1]


def test_fresh_repository_template_is_self_consistent() -> None:
    manifest = (ROOT / "templates/fresh-repository/.jarvas/engineering.yml").read_text(
        encoding="utf-8"
    )
    workflow = (ROOT / "templates/fresh-repository/.github/workflows/jds.yml").read_text(
        encoding="utf-8"
    )

    assert "name: PROJECT_NAME" in manifest
    assert f"platformRef: {PLATFORM_SHA}" in manifest
    assert "enabled: false" in manifest
    assert "security.secret-scan" in manifest
    assert "release.evidence" in manifest
    assert f"@{PLATFORM_SHA}" in workflow
    assert "JDS baseline gate" in workflow


def test_shipped_consumer_examples_do_not_reference_unreleased_tag() -> None:
    paths = [
        ROOT / "templates/consumer-ci.yml",
        ROOT / "examples/engineering.yml",
    ]

    for path in paths:
        content = path.read_text(encoding="utf-8")
        assert "v0.1.0" not in content
        assert PLATFORM_SHA in content
