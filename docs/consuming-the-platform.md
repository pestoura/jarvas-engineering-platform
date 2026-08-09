# Consuming Jarvas Engineering Platform

## Repository access model

The reusable Jarvas Engineering Platform layer is public so both public and private Jarvas/Hermes repositories can resolve its actions and reusable workflows.

The public layer must contain only reusable engineering logic, schemas, standards, generic policy and non-sensitive defaults. Project secrets, private target inventories, credentials, environment-specific sensitive policy and private extensions remain in the consuming repository or a separate private policy/extensions repository.

## Pinning

Consumers must pin a release tag or immutable SHA. Do not consume mutable `main`.

Preferred after the first accepted release:

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
