# Consuming Jarvas Engineering Platform

## Repository access prerequisite

Because this platform repository is private, GitHub Actions access must be enabled in:

`Settings → Actions → General → Access → Accessible from repositories owned by 'pestoura' user`

Only private caller repositories can consume workflows/actions from this private repository. Public caller repositories require a public reusable-workflow source or an alternative distribution model.

## Pinning

Consumers must pin a release tag or immutable SHA. Do not consume mutable `main`.

Preferred during the pilot:

```yaml
uses: pestoura/jarvas-engineering-platform/.github/actions/plan@v0.1.0
```

For higher assurance, pin the exact commit SHA.

## Project manifest

Create `.jarvas/engineering.yml` from `examples/engineering.yml` and declare:

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
