# Capability Request Protocol

Use this when a capsule agent hits a real scope boundary.

Do not keep exploring indefinitely.
Do not make ad hoc requests in prose-only form.

## Trigger Conditions
- need to write outside `allowed_paths`
- need a new API or SPI contract
- need assembly wiring
- need config or IO changes
- need a decision that materially changes player-facing behavior

## Required Output
Create one capsule-local log entry and include these sections:

```markdown
## Needed Capability
## Why Capsule Scope Is Insufficient
## Smallest Change Required
## Impacted Paths / Modules
## Save / Schema Risk
## Suggested Repo-Agent Packet
```

## Suggested Repo-Agent Packet
Keep it short and bounded:
- objective
- required paths
- exact contract or wiring gap
- why the capsule cannot proceed without it

## Rule
Bundle all discovered capability gaps into one log entry when possible.
Do not stop-start repeatedly for one feature.
