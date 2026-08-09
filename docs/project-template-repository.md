# Jarvas Project Template Repository

## Purpose

The recommended way to create a new Jarvas/JDS project is a dedicated GitHub Template Repository, expected at:

```text
pestoura/jarvas-project-template
```

The template repository is a bootstrap surface only. It must not copy the implementation of JDS, shared actions, capability catalogues or reusable workflows into every project.

```text
jarvas-project-template          -> bootstrap files
jarvas-engineering-platform      -> reusable engineering implementation
project repository               -> product/domain-specific code and gates
```

## Canonical source

The canonical minimal JDS bootstrap lives in:

```text
templates/fresh-repository/
```

The external template repository must mirror the following files from that source:

- `README.md`;
- `.jarvas/engineering.yml`;
- `.github/workflows/jds.yml`.

It may additionally contain repository-neutral collaboration/bootstrap files such as `.editorconfig`, `.gitignore`, `SECURITY.md`, `CONTRIBUTING.md`, a pull-request template and empty architecture/ADR documentation scaffolding.

It must not contain language/framework/runtime assumptions such as `pyproject.toml`, `package.json`, Dockerfiles, Terraform roots, Playwright configuration or MCP-specific contracts unless the user explicitly chooses a specialized template later.

## GitHub Template Repository behavior

GitHub's generic **New repository** flow creates a normal empty repository. A project receives this bootstrap only when created through the template repository's **Use this template** flow (or through a controller/API that copies the canonical bootstrap).

GitHub does not interpolate repository names into copied files. For that reason the canonical manifest uses:

```yaml
metadata:
  name: AUTO
```

and workflow evidence records the authoritative runtime identity from `github.repository`.

## New-project baseline

A newly created project starts deliberately neutral:

- project-type detection disabled;
- no Python/Node/MCP/browser/container/infra assumption;
- mandatory repository secret scanning;
- JDS delivery evidence;
- manual release strategy;
- no live-acceptance claim.

When a real implementation slice begins, a normal PR enables detection and/or adds the applicable capabilities.

## Drift policy

The external template repository is a consumer of this platform, not an independent source of truth.

1. It pins the platform to an immutable accepted SHA or release tag.
2. Changes to the canonical fresh bootstrap land here first and pass platform CI.
3. The template repository is updated through a normal PR.
4. A template-contract workflow compares the mirrored canonical files with the pinned platform source.
5. Existing projects are not rewritten when the template changes; they continue consuming the platform through their own version pin and upgrade normally.

## Recommended creation flow

```text
jarvas-project-template
        |
        +-- Use this template
                |
                v
        new repository
                |
                v
        JDS baseline workflow
                |
          +-----+-----+
          |           |
       security     evidence
          |           |
          +-----+-----+
                v
             GREEN
                |
                v
        first vertical slice
                |
                v
      capabilities enabled
```

## Mature repositories

Do not recreate mature repositories from the template. Adopt JDS incrementally using the parity-first process documented in `docs/consuming-the-platform.md`.
