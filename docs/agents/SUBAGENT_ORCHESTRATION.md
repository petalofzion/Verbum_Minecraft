# Subagent Orchestration (Codex Executor Adapter)

This document is the Codex-specific executor guide that implements
[`docs/agents/ORCHESTRATION_SPEC.md`](./ORCHESTRATION_SPEC.md).

Use the orchestration spec for the policy.
Use this document for the command shape, output capture, and Codex-specific validation flow.

## Non-Interactive Spawn (Required)
Use `codex exec` only.
Interactive `codex` sessions are not acceptable for automated orchestration.

Preferred wrapper:

```bash
python3 tools/scripts/codex_exec_from_packet.py path/to/task-packet.json \
  --model gpt-5.3-codex \
  --reasoning-effort medium \
  --report-output subagent_temp/<TASK_ID>.json
```

The wrapper validates the task packet before execution and validates the final report after execution.
For guarded autonomous runs, also pass active-packet and report-history directories so overlap and loop-brake checks are enforced in code:

```bash
python3 tools/scripts/codex_exec_from_packet.py path/to/task-packet.json \
  --model gpt-5.3-codex \
  --reasoning-effort medium \
  --report-output subagent_temp/reports/<TASK_ID>.json \
  --active-packets-dir subagent_temp/active_packets \
  --history-dir subagent_temp/report_history
```

Required command shape:

```bash
codex exec -m <MODEL> -c model_reasoning_effort="<EFFORT>" \
  --sandbox workspace-write --color never \
  --output-schema docs/agents/schemas/agent-report.schema.json \
  --output-last-message subagent_temp/<TASK_ID>.json \
  "YOUR PROMPT HERE"
```

The prompt must instruct the agent to end immediately after completion or when a stop condition fires.

## Required Inputs
Every subagent run must include:
- a task packet that follows [`docs/agents/schemas/task-packet.schema.json`](./schemas/task-packet.schema.json),
- the final report schema at [`docs/agents/schemas/agent-report.schema.json`](./schemas/agent-report.schema.json),
- explicit allowed write paths,
- explicit stop conditions,
- explicit required checks.
- explicit `verification_scope` so the subagent knows whether it owns only capsule-local proof or full repo integration.

Do not send vague freeform prompts for integration work.
Use [`tools/scripts/validate_agent_json.py`](../../tools/scripts/validate_agent_json.py) if you need to validate packets or reports manually.
Use [`tools/scripts/verify_orchestration_run.py`](../../tools/scripts/verify_orchestration_run.py) to enforce:
- allowed-path ownership,
- active packet overlap checks,
- required-check evidence,
- verification-scope discipline,
- loop-brake history checks,
- optional git diff vs `files_touched` validation.

## Required Subagent Temp Folder
All final report files must be written under `subagent_temp/` in repo root.

```bash
mkdir -p subagent_temp
```

Use one unique report filename per run.
Do not reuse a prior report path for a new task.
Recommended layout:
- `subagent_temp/active_packets/` for packets currently in flight
- `subagent_temp/reports/` for the latest report artifact
- `subagent_temp/report_history/` for prior report snapshots used by loop-brake checks

## Model Selection (Required)
Pick the model explicitly for every run.

Recommended defaults:
- `low`: tightly-scoped read-only summaries or simple edits with literal instructions.
- `medium`: default for most capsule tasks.
- `high`: debugging, refactors, or partially-specified repo work.
- `xhigh`: only for unusually ambiguous or complex architectural work.

Every run must set both:
- `-m <MODEL>`
- `-c model_reasoning_effort="<EFFORT>"`

## Prompt Structure
The prompt should mirror the task packet instead of improvising.

Minimum structure:

```text
You are a <capsule|repo> agent.
Task ID: <task_id>
Start at AGENTS.md and follow the required read order.
Allowed write paths: <paths>
You may read additional repo files required by must_read or verification.
Do not modify files outside the allowed write paths.
Objective: <single concrete task>
Must read: <paths>
Success criteria:
- ...
Stop conditions:
- ...
Verification scope: <capsule_local|repo_integration>
Required checks:
- ...
Return a final report that matches docs/agents/schemas/agent-report.schema.json.
End immediately after completion or when any stop condition fires.
```

## Example Spawn
```bash
codex exec -m gpt-5.3-codex -c model_reasoning_effort="medium" \
  --sandbox workspace-write --color never \
  --output-schema docs/agents/schemas/agent-report.schema.json \
  --output-last-message subagent_temp/feature-bible-review.json \
  "You are a capsule agent.
Task ID: feature-bible-review
Start at AGENTS.md and follow the funnel.
Allowed write paths: modules/features/library/bible/**
You may read additional repo files required by must_read or verification.
Do not modify files outside the allowed write paths.
Objective: Review the capsule state and report gaps only.
Must read: FUNNELING.md, modules/features/library/bible/AGENTS.md, docs/contracts/CORE_API.md
Success criteria:
- Identify concrete capsule gaps.
- Do not modify files.
Stop conditions:
- Need to modify files outside the allowed write paths.
- Need a new cross-module contract.
Verification scope: capsule_local
Required checks:
- none
Return task_id exactly as: feature-bible-review
Return a final report that matches docs/agents/schemas/agent-report.schema.json.
Set blocker_category to one of: none, environment, scope, contract, verification, requirements, unknown.
End immediately after completion or when any stop condition fires."
```

## Output Capture (Required)
Always read the final report from the `--output-last-message` file.
Do not trust stdout.

```bash
cat subagent_temp/<TASK_ID>.json
```

Stdout may contain partial reasoning or interim summaries and must not be used as the authoritative result.

## Parallel Runs
Parallel `codex exec` runs are allowed only when:
- they are read-only, or
- they write to disjoint paths and distinct report files.

Never run parallel subagents that can touch:
- the same assembly,
- the same contract surface,
- shared generated indexes,
- the same capsule.

## Validation (Required For Any Changes)
Repo agents must validate any subagent result before integrating it.

Minimum validation:
- inspect `git status --short`,
- inspect the changed files,
- compare `files_touched` in the report to the actual diff,
- run the required checks from the task packet or stronger local checks.

For capsule tasks, the repo agent still owns:
- `tools/scripts/update_todo_index.sh`
- `python3 tools/scripts/update_module_manifest.py`
- full `./gradlew check build`

Recommended command:

```bash
python3 tools/scripts/verify_orchestration_run.py path/to/task-packet.json \
  --report subagent_temp/reports/<TASK_ID>.json \
  --active-packets-dir subagent_temp/active_packets \
  --history-dir subagent_temp/report_history
```

## Loop Brakes
Do not let a subagent continue indefinitely.

If a task needs another round, issue a new task packet when:
- the prior run reported `blocked`, `needs_contract`, or `needs_review`,
- required checks failed without a new hypothesis,
- the task scope changed,
- the agent hit `max_iterations`.

Do not respond to a stale task with "keep going" unless the constraints changed.

## Common Failure Modes
- `TTY` errors: use `codex exec`, not interactive `codex`.
- No report file: verify `--output-last-message` path and prompt termination instructions.
- Scope drift: compare the diff to `allowed_paths`.
- Prose-only report: require the schema and reject non-structured output.
- Executor thrash: stop and re-issue a tighter task packet instead of waiting for more wandering.
