# Orchestrator Quickstart

This is the one-page runbook for a fresh repo agent acting as an orchestrator.

Use this document when the task requires planning, spawning capsule agents, integrating their work, and carrying the loop to completion without mid-run user updates.

## Read Order
1. `AGENTS.md`
2. `docs/agents/REPO_AGENT.md`
3. `WORKFLOW.md`
4. `docs/agents/ORCHESTRATION_SPEC.md`
5. `docs/agents/SUBAGENT_ORCHESTRATION.md`
6. `docs/PROFILE_MODEL.md`
7. `docs/CONTENT_STYLE_BIBLE.md`
8. `docs/UPDATE_SURFACES.md`
9. `docs/CAPSULE_INDEX.md`
10. `docs/GOTCHAS.md`

## Operating Mode
- Own the full loop: `plan -> dispatch -> review -> repair -> verify -> integrate`.
- Do not stop for progress updates.
- Spawn capsule agents only for disjoint write scopes.
- Keep integration, index refreshes, and full repo verification as repo-agent work unless a packet explicitly delegates `repo_integration`.
- When a task adds or changes a repo-level seam, split it into:
  - repo-seam implementation
  - verifier pass
  - capsule implementation

## Default Autonomy Policy
- Keep iterating until the task is complete and integrated.
- Do not ask for permission between normal repair/review cycles.
- Stop only for terminal blockers:
  - missing requirements,
  - materially ambiguous product direction,
  - new cross-module contract with no clear intended shape,
  - repeated no-progress loop,
  - legal/clean-room issue.

## Spawn Rules
- Prefer one packet per capsule or bounded repo surface.
- Use a verifier agent or verifier packet after assembly/core-api seam work.
- Require an architecture audit in the verifier packet when a task changes assemblies, API/SPI seams, or feature-to-assembly behavior routing.
- Do not confuse required reading with open-ended discovery. Once a worker has completed the packet's `must_read` set and named target files, it should implement or stop on a concrete blocker rather than keep hunting precedents.
- Always set:
  - `task_id`
  - `role`
  - `allowed_paths`
  - `must_read`
  - `success_criteria`
  - `stop_conditions`
  - `required_checks`
  - `verification_scope`
  - `max_iterations`
  - `report_schema`
- Use `verification_scope: capsule_local` by default for capsule agents.

## Required Subagent Command
```bash
python3 tools/scripts/codex_exec_from_packet.py path/to/task-packet.json \
  --model gpt-5.3-codex \
  --reasoning-effort medium \
  --report-output subagent_temp/reports/<TASK_ID>.json \
  --active-packets-dir subagent_temp/active_packets \
  --history-dir subagent_temp/report_history
```

## Review Loop
After every subagent finishes:
1. Validate the structured report.
2. Inspect the diff against `allowed_paths`.
3. Decide:
   - integrate as-is,
   - repair locally,
   - issue a tighter follow-up packet,
   - stop on a terminal blocker.

Verifier result handling:
- Treat verifier failure as a normal iteration trigger, not as user-facing closeout.
- If the verifier finds a fixable implementation or integration gap, issue the next corrective packet and continue the loop.
- If the verifier reports boundary drift between assemblies, API/SPI, and capsules, treat that as a real failure surface, not an optional style note.
- Report back to the user only when:
  - the verifier gate is green, or
  - a true terminal blocker prevents further progress.

Do not trust prose summaries without checking the actual file changes and required checks.

## Integration Checklist
- Refresh:
  - `python3 tools/scripts/update_module_manifest.py`
  - `python3 tools/scripts/update_capsule_index.py`
  - `tools/scripts/update_todo_index.sh`
  - `tools/scripts/update_contract_index.sh` when wiring/contracts changed
- Run `./gradlew check build`
- Run targeted assembly build(s) for touched editions
- Run a targeted runtime smoke check when assemblies or core contracts changed
- If the task required verifier signoff, run `python3 tools/scripts/verify_done_gate.py ...` before reporting done
- Confirm profile placement and upward inheritance are correct
- Confirm `docs/UPDATE_SURFACES.md` obligations were satisfied

## Done Means
- code and docs implemented,
- subagent output reviewed,
- verifier signoff present when required,
- generated indexes refreshed,
- `./gradlew check build` passes,
- final diff matches the objective,
- no unresolved loop-brake or scope-drift issues remain.
