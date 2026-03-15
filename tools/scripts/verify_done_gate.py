#!/usr/bin/env python3
import argparse
from pathlib import Path

from json_schema_utils import SchemaValidationError, validate_file


def load_json(repo_root: Path, schema_rel: str, json_path: str | Path) -> dict:
    schema = repo_root / schema_rel
    path = Path(json_path)
    if not path.is_absolute():
        path = (repo_root / path).resolve()
    return validate_file(schema, path)


def command_satisfies(required_command: str, commands_run: list[str]) -> bool:
    return any(
        command == required_command or required_command in command
        for command in commands_run
    )


def main():
    parser = argparse.ArgumentParser(
        description="Verify that a task is allowed to close out as done, including verifier signoff when required."
    )
    parser.add_argument("--task-packet", required=True)
    parser.add_argument("--task-report", required=True)
    parser.add_argument("--verifier-packet")
    parser.add_argument("--verifier-report")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    errors: list[str] = []

    try:
        task_packet = load_json(repo_root, "docs/agents/schemas/task-packet.schema.json", args.task_packet)
        task_report = load_json(repo_root, "docs/agents/schemas/agent-report.schema.json", args.task_report)
    except SchemaValidationError as exc:
        raise SystemExit(str(exc))

    if task_report["task_id"] != task_packet["task_id"]:
        errors.append("Task packet/report task_id mismatch.")
    if task_report["status"] != "done":
        errors.append("Primary task report is not in status 'done'.")

    if task_packet.get("requires_verifier"):
        if not args.verifier_packet or not args.verifier_report:
            errors.append("Task requires verifier signoff but verifier packet/report were not provided.")
        else:
            try:
                verifier_packet = load_json(repo_root, "docs/agents/schemas/task-packet.schema.json", args.verifier_packet)
                verifier_report = load_json(repo_root, "docs/agents/schemas/agent-report.schema.json", args.verifier_report)
            except SchemaValidationError as exc:
                raise SystemExit(str(exc))

            if verifier_packet["role"] != "verifier":
                errors.append("Verifier packet role must be 'verifier'.")
            if verifier_report["task_id"] != verifier_packet["task_id"]:
                errors.append("Verifier packet/report task_id mismatch.")
            if verifier_report["status"] != "done":
                errors.append("Verifier report is not in status 'done'.")
            targets = verifier_packet.get("verification_targets") or []
            if task_packet["task_id"] not in targets:
                errors.append("Verifier packet does not list the task_id in verification_targets.")
            for required_check in verifier_packet["required_checks"]:
                if required_check.strip().lower() == "none":
                    continue
                if not command_satisfies(required_check, verifier_report["commands_run"]):
                    errors.append(f"Verifier report is missing required check: {required_check}")
            if verifier_packet.get("gotcha_review_required") and not verifier_report.get("gotchas_checked"):
                errors.append("Verifier packet requires gotcha review but verifier report.gotchas_checked is empty.")

    if errors:
        raise SystemExit("\n".join(errors))

    print("Verified: Done gate is satisfied.")


if __name__ == "__main__":
    main()
