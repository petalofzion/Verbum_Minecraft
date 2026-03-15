# Verbum Verifier Packet Template

Use this when you want a verifier agent to validate work without implementing fixes.

```md
# VERIFIER PACKET

## Assumed agent role
verifier

## Task
<short verification title>

## Verification target(s)
- <task_id or implementation scope>

## Mission
Validate the implementation and report only. Do not edit implementation files.

## Inputs
- Read:
  - `AGENTS.md`
  - `docs/agents/VERIFIER_AGENT.md`
  - `docs/agents/ORCHESTRATION_SPEC.md`
  - `docs/UPDATE_SURFACES.md`
  - `docs/GOTCHAS.md`
- Inspect only the touched code and relevant reports.

## Allowed authority
- run verification commands
- inspect logs, crash reports, and generated surfaces
- report failures clearly

## Prohibited authority
- do not implement fixes
- do not broaden scope
- do not silently rewrite code

## Required checks
- `./gradlew check build`
- targeted assembly build(s): `<required | inspect | no>`
- targeted runtime smoke: `<required | inspect | no>`

## Gotcha review
- required: `<yes | no>`
- touched gotcha surfaces:
  - ...

## Done means
- all required checks were run
- the report identifies the smallest failing surface or confirms green status
- no implementation files were edited

## Final report
Include:
- exact commands run
- pass/fail result
- gotchas checked
- smallest failing surface
- whether the issue is capsule, repo wiring, runtime/version, or environment
```
