# Consuming Jarvas Engineering Platform

## Repository access model

The reusable Jarvas Engineering Platform layer is public so both public and private Jarvas/Hermes repositories can resolve its actions and reusable workflows.

The public layer must contain only reusable engineering logic, schemas, standards, generic policy and non-sensitive defaults. Project secrets, private target inventories, credentials, environment-specific sensitive policy and private extensions remain in the consuming repository or a separate private policy/extensions repository.

## Pinning

Consumers must pin a release tag or immutable SHA. Do not consume mutable `main`.

Current accepted baseline:

```text
9ee1147ea85bbb5bbb733d252bab9ccbb113f5ef
```

Until a human-readable release tag exists, examples and templates use that immutable SHA. After the first accepted tag is created, consumers may move through a normal validated upgrade PR.

## Fresh repositories

For new projects, the preferred path is the dedicated GitHub Template Repository documented in [`project-template-repository.md`](project-template-repository.md), expected as `pestoura/jarvas-project-template`.

Creating a repository with GitHub's generic **New repository** flow creates an empty repository. GitHub does not automatically copy JDS files from this repository.

A fresh repository must therefore be created through **Use this template** or initialized from `templates/fresh-repository/` by an automation/controller. The fresh baseline deliberately starts with only:

- JDS manifest validation/planning;
- mandatory repository security/secret scanning;
- exact-SHA delivery evidence.

Project-type detection is initially disabled so a brand-new repository does not claim or execute Python, Shell, container, browser or schema capabilities before corresponding project structure exists. The template manifest uses `metadata.name: AUTO` because GitHub does not substitute the target repository name into copied files. When implementation begins, enable detection and/or declare the appropriate preset/capabilities in a normal PR.

## Mature repositories

For an existing project, create `.jarvas/engineering.yml` from `examples/engineering.yml` and adopt reusable workflows or check-name-preserving composite actions incrementally. Do not retire established project-local gates until central parity is proven.

The manifest declares:

- JDS version;
- platform version;
- criticality;
- optional preset;
- explicit capability additions/removals;
- release and live-acceptance policy.

Execution strategy is informational and does not change engineering/security policy.

## Integration model

The recommended orchestration is:

```text
planner
  ├─ docs quality (if selected)
  ├─ Python quality (if selected)
  ├─ Shell quality (if selected)
  ├─ schema/config validation (if selected)
  └─ repository security (if selected)
             ↓
         fast-gate
             ↓
  container/runtime assurance (if selected)
             ↓
 project-specific live/release gates
```

The planner output is evidence: selected/skipped capabilities, selected gates, criticality, changed files, classification and ambiguity state are all explicit.

## Migration rule

Do not remove a mature project-local gate merely because a central equivalent exists. First run the central implementation additively, compare outcomes, and remove the local implementation only after parity is proven and documented.

## Sensitive extensions

If a project later needs shared logic that must remain private, keep that logic outside this public reusable layer. A separate `jarvas-engineering-policy-private` repository may be introduced if cross-project private policy reuse becomes necessary.
