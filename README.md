# Jarvas Engineering Platform

Reusable engineering standards, capability catalogues and GitHub Actions workflows for the Jarvas/Hermes portfolio.

## Purpose

This repository is the central implementation of **JDS-001**. It provides reusable delivery primitives without forcing projects into closed profiles or fixed execution topologies.

Core principles:

- capabilities are composable;
- presets are optional shortcuts, never mandatory project categories;
- project-local overrides remain authoritative where risk requires them;
- concurrency follows independent critical-path work, with bounded WIP rather than mandatory lanes or agents;
- gates are selected from risk, capabilities and change impact;
- cheap deterministic gates run before expensive acceptance where that improves time-to-first-failure without unnecessarily increasing time-to-GREEN;
- skipped gates must be explicit and auditable;
- central workflows are version-pinned by consuming repositories.

The initial bootstrap is intentionally minimal. The next change introduces the JDS-001 source of truth, schemas, capability catalogue, planner and reusable workflow baseline.