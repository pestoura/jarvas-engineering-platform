# Jarvas Engineering Platform

Central engineering standards, capability catalogue, gate planner and reusable GitHub Actions workflows for the Jarvas/Hermes portfolio.

## JDS-001

This repository is the executable implementation of **JDS-001**. It deliberately avoids closed project profiles and fixed execution topologies.

```text
STANDARD
   +
CAPABILITIES
   +
OPTIONAL PRESET
   +
PROJECT OVERRIDES
   +
RISK / CRITICALITY
   +
CHANGE IMPACT
   ↓
EFFECTIVE GATE PLAN
```

Core properties:

- capabilities are composable;
- presets are optional shortcuts;
- mandatory risk policy cannot be removed by project configuration;
- unknown/ambiguous change impact fails safe to the full applicable plan;
- bounded WIP replaces mandatory lane counts;
- the Integration Controller is a role, not an agent requirement;
- central workflows are version-pinned by consumers;
- project-local gates remain until central parity is proven;
- skipped gates are explicit and auditable.

## Repository layout

```text
.jarvas/engineering.yml                 self-hosted platform manifest
catalog/capabilities.yml                capabilities + optional presets
schemas/                                manifest contracts
docs/JDS-001.md                         canonical delivery standard
docs/gate-selection.md                  capability/risk/change selection model
.github/actions/plan/                    executable gate planner action
.github/workflows/reusable-*.yml         reusable quality/security/assurance jobs
templates/consumer-ci.yml                reference consumer orchestration
tests/                                  policy/planner regression tests
```

## Gate planner

The planner validates `.jarvas/engineering.yml`, reconciles policy, explicit capabilities, preset, auto-detection and changed paths, then emits:

- effective capabilities;
- selected capabilities;
- selected gates;
- skipped capabilities and reasons;
- criticality;
- changed files;
- docs-only classification;
- ambiguity/fail-safe state.

Catch-all controls such as secret scanning and release evidence do **not** count as change classification signals, preventing unknown changes from being incorrectly treated as understood.

## Reusable workflows

Initial reusable primitives:

- `reusable-python-quality.yml`
- `reusable-shell-quality.yml`
- `reusable-schema-quality.yml`
- `reusable-docs-quality.yml`
- `reusable-repository-security.yml`
- `reusable-container-assurance.yml`

Browser, Security Lab and product-specific live acceptance remain project-controlled until central implementations demonstrate parity.

## Consumption

The reusable layer is public so both public and private Jarvas/Hermes repositories can consume it without exposing project secrets or private runtime policy.

Consumers must pin a release tag or immutable SHA. See `docs/consuming-the-platform.md` and `templates/consumer-ci.yml`.

The first release target is `v0.1.0`, followed by additive parity pilots before any mature project-local gate is retired.
