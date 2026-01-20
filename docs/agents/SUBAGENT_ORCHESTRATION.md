# Subagent Orchestration (Repo Agent Guide)

This guide defines the **only supported** way for repo agents to spawn Codex subagents,
capture their final output, and validate their work without manual TUI interaction.

## Goals
- Run subagents **non-interactively**.
- Capture a **single final report** to a file.
- Keep subagents siloed to their task scope.
- Verify changes independently (do not trust stdout).

## Non-Interactive Spawn (Required)
Use `codex exec` with `--output-last-message` and a prompt that ends with “stop”.

```bash
codex exec --sandbox workspace-write --color never \
  --output-last-message subagent_temp/REPORT.txt \
  "YOUR PROMPT HERE"
```

### Why this is required
- `codex "prompt"` (interactive) **requires a TTY** and fails in automation.
- `codex exec` runs immediately and can be automated.
- `--output-last-message` writes the final response to a file you can parse.

## Required Subagent Temp Folder
All subagent outputs must go in `subagent_temp/` at repo root.

```bash
mkdir -p subagent_temp
```

All `--output-last-message` files **must** be written under `subagent_temp/`.
Use a unique filename per run to avoid overwriting reports.

## Model Selection (Required)
Pick a model explicitly when spawning subagents. Use faster/cheaper models for
simple reads or summaries, and higher‑reasoning models for debugging, refactors,
or architectural changes.

### Set model on the command
```bash
codex exec -m <MODEL> --sandbox workspace-write --color never \
  --output-last-message subagent_temp/REPORT.txt \
  "YOUR PROMPT HERE"
```

Equivalent:
```bash
codex exec -c model="<MODEL>" --sandbox workspace-write --color never \
  --output-last-message subagent_temp/REPORT.txt \
  "YOUR PROMPT HERE"
```

### How to list available model names
There is no non‑interactive `codex` CLI command that prints a model list.
Use the interactive picker:
```bash
codex
# then run:
/model
```

If you manage profiles, you can also set model defaults in
`~/.codex/config.toml` and select them with `-p <PROFILE>`.

## Reasoning Effort (Cost/Latency Control)
You can set reasoning depth per run. Lower effort is cheaper/faster; higher
effort is slower/more expensive but better for complex debugging.

```bash
codex exec -m gpt-5.2-codex -c model_reasoning_effort="low" \
  --sandbox workspace-write --color never \
  --output-last-message subagent_temp/REPORT.txt \
  "YOUR PROMPT HERE"
```

Supported values (from config): `low`, `medium`, `high`, `xhigh`.
You can set a default in `~/.codex/config.toml` or use profiles via `-p`.

### How to choose reasoning effort (required)
- `low`: Use only for **simple, tightly‑specified tasks** with explicit steps.
  The prompt must be highly specific and literal.
- `medium`: Default for most tasks. Works well with normal instructions and
  moderate context.
- `high`: Use for complex changes, debugging, or partial specs.
- `xhigh`: Reserved for **very complex** tasks with unclear or evolving specs.

All subagent runs **must** explicitly set both the model and
`model_reasoning_effort`.

## Prompt Templates
All prompts must:
- Explicitly state the agent role (capsule or repo).
- Instruct the agent to start at `AGENTS.md` and follow the full funneling
  pipeline from there.
- Enforce scope boundaries in the prompt.

### Capsule review (read-only)
```text
You are a capsule agent. Start at AGENTS.md and follow the funnel.
Your scope is only modules/features/<domain>/<feature>/**.
Task: review the capsule state (code, resources, docs, TODO, agent logs).
Do not modify files. Do not run build/tests. Report findings and files read.
End immediately after the report.
```

### Capsule task (changes allowed)
```text
You are a capsule agent. Start at AGENTS.md and follow the funnel.
Your scope is only modules/features/<domain>/<feature>/**.
Task: <describe changes>. Use only contracts in docs/contracts/CORE_API.md.
If a capability is missing, do a capability sweep, log it in docs/agent-logs/,
then stop. Run capsule commands listed in the capsule AGENTS.md.
End immediately after the final report.
```

### Repo task (wiring/integration)
```text
You are a repo agent. Follow the repo agent read order in AGENTS.md.
Task: <describe wiring work>. Respect restricted areas and architecture rules.
Do not modify files outside the task scope. End immediately after the report.
```

## Output Capture (Required)
Always read the final report from the output file, not stdout.

```bash
cat subagent_temp/REPORT.txt
```

### Do not trust stdout
The CLI prints internal "thinking" and interim summaries to stdout.
Those are **not** the final report and can be wrong.

## Parallel Subagents (Allowed, With Constraints)
You can run multiple `codex exec` processes in parallel **only** when they:
- are read‑only, or
- write to **disjoint files** (no overlap).

Never run parallel subagents that might edit the same file or shared index.

### Parallel example (read‑only summaries)
```bash
codex exec -m gpt-5.2-codex -c model_reasoning_effort="low" \
  --sandbox workspace-write --color never \
  --output-last-message subagent_temp/readme_summary.txt \
  "Summarize README.md in 5 concise bullets. Do not modify files. End immediately." &

codex exec -m gpt-5.2-codex -c model_reasoning_effort="low" \
  --sandbox workspace-write --color never \
  --output-last-message subagent_temp/todo_summary.txt \
  "Summarize TODO.md in 5 concise bullets. Do not modify files. End immediately." &

wait
```

## Validation (Required for any changes)
Subagents can write incorrect files (example: invalid syntax).
Repo agents **must verify** any created or modified file.

Minimum checks:
- `git status --short`
- `rg` or `sed` to inspect changed files
- Format/lint/test commands if the task demands it

Example:
```bash
rg -n "" THROWAWAY.py
python3 -m py_compile THROWAWAY.py
```

## Timeouts and Stuck Sessions
If `codex exec` does not exit, terminate it.

Example timeout:
```bash
timeout 120s codex exec --sandbox workspace-write --color never \
  --output-last-message subagent_temp/REPORT.txt \
  "YOUR PROMPT HERE"
```

If needed, kill by PID:
```bash
ps -ax | rg "codex exec"
kill <PID>
```

## Optional Structured Output
For machine parsing, provide a JSON schema and use `--output-schema`.
This forces the final report to match your required structure.

Example schema (minimal):
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["summary", "files_read", "issues"],
  "properties": {
    "summary": { "type": "string" },
    "files_read": { "type": "array", "items": { "type": "string" } },
    "issues": { "type": "array", "items": { "type": "string" } }
  }
}
```

Example usage:
```bash
codex exec -m gpt-5.2-codex -c model_reasoning_effort="medium" \
  --sandbox workspace-write --color never \
  --output-schema subagent_temp/report_schema.json \
  --output-last-message subagent_temp/REPORT.json \
  "YOUR PROMPT HERE"
```

## Common Failure Modes
- **TTY errors:** use `codex exec` only.
- **No final report file:** verify `--output-last-message` path.
- **Incorrect file content:** always validate output before accepting.
- **Scope drift:** enforce scope in the prompt and verify file paths touched.

## Clean-Up (Recommended)
If the task was a test, remove artifacts after validation:
```bash
rm -f THROWAWAY.py
```
