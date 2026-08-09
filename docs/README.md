# Documentation index

This directory contains the canonical engineering documentation for the Jarvas Engineering Platform.

## Read first

1. [`00-platform-overview.md`](00-platform-overview.md) — purpose, current capabilities, boundaries and architecture views.
2. [`JDS-001.md`](JDS-001.md) — canonical engineering/delivery standard.
3. [`consuming-the-platform.md`](consuming-the-platform.md) — how a repository consumes the platform safely.
4. [`gate-selection.md`](gate-selection.md) — how capabilities, risk and change impact become an effective gate plan.
5. [`project-template-repository.md`](project-template-repository.md) — relationship with `jarvas-project-template`.

## Sources of truth

| Concern | Canonical source |
|---|---|
| Engineering standard | `docs/JDS-001.md` |
| Capability/preset definitions | `catalog/capabilities.yml` |
| Project manifest contract | `schemas/project-engineering-profile.schema.json` |
| Gate-selection implementation | `.github/actions/plan/planner.py` |
| Reusable CI implementation | `.github/workflows/reusable-*.yml` |
| Consumer examples | `templates/` and `examples/` |

## Documentation maintenance rule

Documentation must distinguish **implemented platform capability** from **recommended consumer practice** and from **future platform evolution**. A workflow or capability is only described as executable when corresponding repository code exists. Project-specific acceptance remains owned by each consumer until central parity is explicitly demonstrated.
