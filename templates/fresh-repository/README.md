# Project

Repository initialized from the Jarvas Engineering Platform fresh-project baseline.

The initial baseline intentionally enables only JDS planning, mandatory repository security and delivery evidence. It does not assume a programming language, framework, runtime, deployment target or execution strategy.

When implementation begins, enable auto-detection and/or add only the capabilities the project actually needs in `.jarvas/engineering.yml`.

## First delivery slice

1. Define the product objective and next usable baseline.
2. Add only the minimum project structure required for that vertical slice.
3. Enable or declare the corresponding engineering capabilities.
4. Let JDS select the applicable gates from risk + capabilities + change impact.
5. Keep project-specific acceptance gates local until a central equivalent has proven parity.

The manifest uses `metadata.name: AUTO` because GitHub Template Repositories do not substitute repository names into copied files. Runtime evidence uses GitHub's actual `${{ github.repository }}` identity.
