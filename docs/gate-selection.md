# JDS-001 Gate Selection

The platform derives the effective gate plan from four inputs:

```text
mandatory risk policy
        +
explicit capabilities
        +
optional preset / auto-detection
        +
change impact
        ↓
EFFECTIVE GATE PLAN
```

Precedence:

```text
MANDATORY POLICY > EXPLICIT CONFIG > PRESET DEFAULTS > AUTO-DETECTION
```

Change-aware optimization may skip only gates declared safe to skip for the observed change class. It may never remove a mandatory risk or release gate.

## Examples

### Documentation-only

Run documentation/contracts and secret scanning. Avoid image/runtime/browser acceptance unless the changed documentation is itself a runtime source of truth or a project-local contract requires the heavier gate.

### Python implementation

Run compile, lint, typing/schema as applicable, targeted/full tests, secret/SCA/SAST as selected, then package/integration only when affected.

### Docker/base-image

Run image build, provenance, image vulnerability scan, SBOM and isolated acceptance when the project declares those capabilities.

### Browser/UI contract

Run semantic/UI contract tests, worker/session isolation, controlled browser acceptance and live attestation only when promotion requires it.

### Security Lab environment/network

Run registry/schema, isolation, readiness, scenario/reset and host-safety controls.

## Fail-safe

If impact classification is ambiguous:

```text
RUN THE GATE
```

## Plan evidence

Every planner result records:

- effective capabilities;
- selected gates;
- skipped capabilities/gates and reason;
- policy/manifest version;
- criticality;
- changed files;
- ambiguity/fail-safe state.

The objective is to optimize both **time-to-first-failure** and **time-to-GREEN**. JDS-001 therefore uses dependency-aware DAGs rather than either unconditional parallelism or unconditional serialization.