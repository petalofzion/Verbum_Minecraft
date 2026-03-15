#!/usr/bin/env python3
import argparse
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
import shutil

from json_schema_utils import SchemaValidationError, validate_file


def build_prompt(packet):
    lines = [
        f"You are a {packet['role']} agent.",
        f"Task ID: {packet['task_id']}",
        "Start at AGENTS.md and follow the required read order.",
        f"Allowed write paths: {', '.join(packet['allowed_paths'])}",
        "You may read additional repo files when required by must_read, verification, or stop-condition handling.",
        "Do not modify files outside the allowed write paths.",
        f"Objective: {packet['objective']}",
        f"Must read: {', '.join(packet['must_read'])}",
        "Success criteria:",
    ]
    lines.extend(f"- {item}" for item in packet["success_criteria"])
    lines.append("Stop conditions:")
    lines.extend(f"- {item}" for item in packet["stop_conditions"])
    lines.append("Required checks:")
    if packet["required_checks"]:
        lines.extend(f"- {item}" for item in packet["required_checks"])
    else:
        lines.append("- none")
    lines.append(f"Return task_id exactly as: {packet['task_id']}")
    lines.append(f"Return a final report that matches {packet['report_schema']}.")
    lines.append("End immediately after completion or when any stop condition fires.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Run codex exec from a validated task packet.")
    parser.add_argument("task_packet", help="Path to the task packet JSON file")
    parser.add_argument("--model", required=True, help="Codex model to use")
    parser.add_argument("--reasoning-effort", default="medium", help="Reasoning effort to pass to codex")
    parser.add_argument("--report-output", required=True, help="Where to write the final report JSON")
    parser.add_argument("--sandbox", default="workspace-write", help="Codex sandbox mode")
    parser.add_argument("--color", default="never", help="Codex color mode")
    parser.add_argument("--executor", default="codex", help="Executor binary name")
    parser.add_argument(
        "--active-packets-dir",
        help="Directory containing other active task packets for overlap validation",
    )
    parser.add_argument(
        "--history-dir",
        help="Directory containing prior report JSON files for loop-brake validation",
    )
    parser.add_argument(
        "--check-git",
        action="store_true",
        help="Validate files_touched against actual git changes within allowed_paths",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print the command without running it")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    packet_path = (repo_root / args.task_packet).resolve() if not Path(args.task_packet).is_absolute() else Path(args.task_packet)
    task_schema = repo_root / "docs/agents/schemas/task-packet.schema.json"

    try:
        packet = validate_file(task_schema, packet_path)
    except SchemaValidationError as exc:
        raise SystemExit(str(exc))

    report_schema = (repo_root / packet["report_schema"]).resolve()
    if not report_schema.exists():
        raise SystemExit(f"Missing report schema: {report_schema}")

    report_output = (repo_root / args.report_output).resolve() if not Path(args.report_output).is_absolute() else Path(args.report_output)
    report_output.parent.mkdir(parents=True, exist_ok=True)

    preflight_command = [
        "python3",
        "tools/scripts/verify_orchestration_run.py",
        str(packet_path.relative_to(repo_root)),
    ]
    if args.active_packets_dir:
        preflight_command.extend(["--active-packets-dir", args.active_packets_dir])

    subprocess.run(preflight_command, cwd=repo_root, check=True)

    prompt = build_prompt(packet)
    command = [
        args.executor,
        "exec",
        "-m",
        args.model,
        "-c",
        f'model_reasoning_effort="{args.reasoning_effort}"',
        "--sandbox",
        args.sandbox,
        "--color",
        args.color,
        "--output-schema",
        packet["report_schema"],
        "--output-last-message",
        str(report_output.relative_to(repo_root)),
        prompt,
    ]

    if args.dry_run:
        print(json.dumps({"command": command, "cwd": str(repo_root)}, indent=2))
        return

    subprocess.run(command, cwd=repo_root, check=True)

    postflight_command = [
        "python3",
        "tools/scripts/verify_orchestration_run.py",
        str(packet_path.relative_to(repo_root)),
        "--report",
        str(report_output.relative_to(repo_root)),
    ]
    if args.active_packets_dir:
        postflight_command.extend(["--active-packets-dir", args.active_packets_dir])
    if args.history_dir:
        postflight_command.extend(["--history-dir", args.history_dir])
    if args.check_git:
        postflight_command.append("--check-git")

    try:
        validate_file(report_schema, report_output)
    except SchemaValidationError as exc:
        raise SystemExit(f"Generated report failed validation:\n{exc}")

    subprocess.run(postflight_command, cwd=repo_root, check=True)

    if args.history_dir:
        history_dir = (repo_root / args.history_dir).resolve() if not Path(args.history_dir).is_absolute() else Path(args.history_dir).resolve()
        history_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        history_path = history_dir / f"{packet['task_id']}-{timestamp}.json"
        shutil.copy2(report_output, history_path)


if __name__ == "__main__":
    main()
