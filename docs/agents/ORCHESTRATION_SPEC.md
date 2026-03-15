# Orchestration Spec

This document defines the repo's model-agnostic orchestration contract for autonomous and semi-autonomous agent work.

Use this spec for the control loop itself.
Use [`docs/agents/SUBAGENT_ORCHESTRATION.md`](./SUBAGENT_ORCHESTRATION.md) only for the Codex-specific executor details.

## Goals
- Keep agent work bounded, terminating, and reviewable.
- Separate orchestration policy from executor implementation.
- Preserve module boundaries while still allowing parallel work.
- Require enough structured evidence that the orchestrator can validate progress instead of trusting prose.

## Control Loop
The orchestrator runs work through these states:

1. `triaged`
2. `task_packet_ready`
3. `dispatched`
4. `executing`
5. `reported`
6. `verified`
7. `integrated`

Terminal states:
- `done`
- `blocked`
- `needs_contract`
- `needs_review`
- `failed`

Recommended execution roles inside the loop:
- `repo` for wiring, contracts, assembly changes, and integration
- `capsule` for siloed module work
- verifier pass for runtime-sensitive or seam-sensitive validation

An agent should never invent a new state. If it cannot satisfy the task within the packet constraints, it must stop in one of the terminal states and report.

## Required Task Packet
Every delegated task must provide a machine-readable packet or a prompt that contains the same fields.
The canonical schema lives at [`docs/agents/schemas/task-packet.schema.json`](./schemas/task-packet.schema.json).

Required fields:
- `task_id`: stable unique identifier for the delegated work item.
- `role`: `capsule` or `repo`.
- `objective`: one-sentence concrete task.
- `allowed_paths`: directories or files the agent may modify.
- `must_read`: docs/files the agent must read before acting.
- `success_criteria`: explicit completion checks.
- `stop_conditions`: explicit reasons to stop and report instead of continuing.
- `required_checks`: commands or validations that must be run before completion unless blocked.
- `verification_scope`: whether delegated verification ends at capsule-local proof or includes repo integration.
- `max_iterations`: maximum self-directed attempt count before the agent must report.
- `report_schema`: path or identifier for the required final report schema.

Optional but recommended:
- `context_bundle`: exact files or notes passed to the agent.
- `handoff_inputs`: dependencies from earlier tasks.
- `priority`: `low`, `normal`, or `high`.
- `requires_verifier`: whether closeout requires a verifier report.
- `verification_targets`: task ids a verifier packet is validating.
- `gotcha_review_required`: whether the verifier must explicitly review `docs/GOTCHAS.md`.

## Context Discipline
Context should be layered, not dumped.

Preferred order:
1. Global invariants: architecture, runtime constitution, clean-room rules.
2. Role guide: capsule or repo.
3. Task packet.
4. Local files relevant to the task.
5. Only then supporting repo context.

Do not flood subagents with repo-wide summaries unless the task genuinely needs them.
The orchestrator owns context curation.

## Final Report Contract
Every agent must return a structured final report that matches
[`docs/agents/schemas/agent-report.schema.json`](./schemas/agent-report.schema.json).

Required report fields:
- `task_id`
- `status`
- `summary`
- `files_touched`
- `files_read`
- `commands_run`
- `evidence`
- `blockers`
- `next_action`

Allowed `status` values:
- `done`
- `blocked`
- `needs_contract`
- `needs_review`
- `failed`

Required report classification:
- `blocker_category`: `none`, `environment`, `scope`, `contract`, `verification`, `requirements`, or `unknown`.

The orchestrator should reject unstructured or incomplete final reports for integration work.

## Stop Conditions
Every task packet must define stop conditions.
At minimum, include these:

- Missing cross-module contract or SPI capability.
- Need to write outside `allowed_paths`.
- Need to change assembly wiring when assigned as a capsule task.
- Repeated verification failure with no new hypothesis.
- No net progress after two consecutive attempts.
- Ambiguous requirement that materially changes data model, public API, or player-facing behavior.

When a stop condition triggers, the agent must end immediately after writing its report.
It should not continue exploring indefinitely.

## Loop Brakes
To avoid autonomous thrashing, the orchestrator must enforce:

- `max_iterations` per task.
- Repeated-summary detection.
- Repeated-file-set detection.
- Repeated-blocker detection.
- No-progress timeout for long-running executor sessions.

Recommended policy:
- If the same blocker appears twice without a new proposed action, stop and escalate.
- If the touched file set does not change across two repair attempts, stop and escalate.
- If required checks fail twice for the same reason, report `needs_review` unless a new fix path is identified.

## Cohesion And Progress Checks
The orchestrator is responsible for validating that delegated work remains coherent.

Minimum checks before integration:
- `files_touched` stay within `allowed_paths`.
- No overlapping write ownership between active agents.
- Required checks actually ran, or the report explains why not.
- Relevant indexes or generated docs are up to date.
- The final diff matches the task objective instead of adjacent speculative work.

Verification ownership:
- `capsule_local`: the subagent proves only capsule-local structure and checks. Repo indexes, manifest refreshes, and full `./gradlew check build` remain repo-agent work.
- `repo_integration`: the delegated task owns integration updates and repo-level verification in addition to local edits.

When to add a dedicated verifier pass:
- any change in `assemblies/*`
- any new or changed contract in `modules/core/api/*` or `modules/core/spi/*`
- any new runtime registration seam
- any task whose first real proof requires client/server initialization rather than pure compilation

Repo-local enforcement is available through `tools/scripts/verify_orchestration_run.py`.
Closeout-gate enforcement is available through `tools/scripts/verify_done_gate.py`.

Recommended checks:
- Compare the report summary to the actual diff.
- Re-run the highest-signal verification locally.
- Confirm that any new stop condition or capability gap is logged in the correct place.
- For repo-seam work, prefer `repo-seam packet -> verifier pass -> capsule packet` over one mixed implementation packet.

## Report-Back Policy
Agents should report back immediately when:
- the task is done,
- a stop condition fires,
- they need a new contract,
- they need a new task packet because scope changed.

Agents should not report back merely because they finished reading context.
The orchestrator should not ask for streaming status unless the executor requires it.

## Parallel Work Rules
Parallel work is allowed only when write scopes are disjoint.

Safe patterns:
- multiple read-only reviews,
- multiple capsule implementations touching different capsules,
- one implementation task plus one read-only validation task.

Unsafe patterns:
- two agents editing the same assembly,
- two agents editing shared indexes,
- two agents editing the same contract surface without a dedicated contract packet.

## Integration Policy
The orchestrator, not the subagent, decides whether work is integrated.

Before integrating:
- validate the diff,
- run the required checks,
- ensure the report status is acceptable,
- ensure the work satisfies the task packet.

If the result is directionally useful but incomplete, create a new task packet instead of telling the same agent to "keep going" without updated constraints.
