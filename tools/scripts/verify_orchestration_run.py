#!/usr/bin/env python3
import argparse
import subprocess
from pathlib import Path

from json_schema_utils import SchemaValidationError, validate_file


def normalize_repo_path(repo_root: Path, path_text: str) -> str:
    path = Path(path_text)
    if path.is_absolute():
        try:
            path = path.resolve().relative_to(repo_root.resolve())
        except ValueError as exc:
            raise ValueError(f"Absolute path is outside repo root: {path_text}") from exc
    normalized = path.as_posix().strip("/")
    if not normalized:
        raise ValueError("Path must not be empty")
    return normalized


def normalize_allowed_prefix(repo_root: Path, allowed_path: str) -> str:
    trimmed = allowed_path
    if trimmed.endswith("/**"):
        trimmed = trimmed[:-3]
    elif trimmed.endswith("/*"):
        trimmed = trimmed[:-2]
    return normalize_repo_path(repo_root, trimmed)


def path_is_within(repo_root: Path, rel_path: str, allowed_path: str) -> bool:
    rel = normalize_repo_path(repo_root, rel_path)
    allowed = normalize_allowed_prefix(repo_root, allowed_path)
    return rel == allowed or rel.startswith(f"{allowed}/")


def paths_overlap(repo_root: Path, left: str, right: str) -> bool:
    left_norm = normalize_allowed_prefix(repo_root, left)
    right_norm = normalize_allowed_prefix(repo_root, right)
    return (
        left_norm == right_norm
        or left_norm.startswith(f"{right_norm}/")
        or right_norm.startswith(f"{left_norm}/")
    )


def git_changed_files(repo_root: Path) -> set[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    changed = set()
    for raw_line in result.stdout.splitlines():
        if not raw_line:
            continue
        line = raw_line[3:]
        if " -> " in line:
            old_path, new_path = line.split(" -> ", 1)
            changed.add(normalize_repo_path(repo_root, old_path))
            changed.add(normalize_repo_path(repo_root, new_path))
        else:
            changed.add(normalize_repo_path(repo_root, line))
    return changed


def load_task_packet(repo_root: Path, packet_path: Path) -> dict:
    schema_path = repo_root / "docs/agents/schemas/task-packet.schema.json"
    return validate_file(schema_path, packet_path)


def load_agent_report(repo_root: Path, report_path: Path) -> dict:
    schema_path = repo_root / "docs/agents/schemas/agent-report.schema.json"
    return validate_file(schema_path, report_path)


def command_satisfies(required_command: str, commands_run: list[str]) -> bool:
    return any(
        command == required_command or required_command in command
        for command in commands_run
    )


def validate_overlap(repo_root: Path, packet: dict, packet_path: Path, active_packets_dir: Path | None) -> list[str]:
    if active_packets_dir is None or not active_packets_dir.exists():
        return []

    errors = []
    for candidate in sorted(active_packets_dir.glob("*.json")):
        if candidate.resolve() == packet_path.resolve():
            continue
        try:
            other = validate_file(
                repo_root / "docs/agents/schemas/task-packet.schema.json",
                candidate,
            )
        except SchemaValidationError as exc:
            errors.append(f"Invalid active task packet {candidate}: {exc}")
            continue

        if other["task_id"] == packet["task_id"]:
            continue

        overlaps = [
            f"{left} <-> {right}"
            for left in packet["allowed_paths"]
            for right in other["allowed_paths"]
            if paths_overlap(repo_root, left, right)
        ]
        if overlaps:
            errors.append(
                "Allowed-path overlap with active task "
                f"{other['task_id']} ({candidate}): {', '.join(overlaps)}"
            )
    return errors


def load_report_history(repo_root: Path, history_dir: Path | None, task_id: str, current_report: Path | None) -> list[tuple[Path, dict]]:
    if history_dir is None or not history_dir.exists():
        return []

    history = []
    schema_path = repo_root / "docs/agents/schemas/agent-report.schema.json"
    for candidate in sorted(history_dir.glob("*.json"), key=lambda path: path.stat().st_mtime):
        if current_report is not None and candidate.resolve() == current_report.resolve():
            continue
        try:
            report = validate_file(schema_path, candidate)
        except SchemaValidationError:
            continue
        if report["task_id"] == task_id:
            history.append((candidate, report))
    return history


def validate_report(
    repo_root: Path,
    packet: dict,
    report: dict,
    history_dir: Path | None,
    report_path: Path,
    check_git: bool,
) -> list[str]:
    errors = []

    if report["task_id"] != packet["task_id"]:
        errors.append(
            f"Task/report mismatch: packet task_id is {packet['task_id']!r}, "
            f"report task_id is {report['task_id']!r}"
        )

    normalized_allowed = [normalize_repo_path(repo_root, path) for path in packet["allowed_paths"]]
    normalized_touched = [normalize_repo_path(repo_root, path) for path in report["files_touched"]]
    normalized_read = [normalize_repo_path(repo_root, path) for path in report["files_read"]]

    if report["status"] in {"done", "needs_review", "failed"}:
        for required_path in packet["must_read"]:
            required_norm = normalize_repo_path(repo_root, required_path)
            if required_norm not in normalized_read:
                errors.append(f"Missing required read in report.files_read: {required_path}")

    for touched_path in normalized_touched:
        if not any(path_is_within(repo_root, touched_path, allowed) for allowed in normalized_allowed):
            errors.append(
                f"Report touched file outside allowed_paths: {touched_path} not in {packet['allowed_paths']}"
            )

    required_checks = [
        check for check in packet["required_checks"]
        if check.strip().lower() != "none"
    ]
    if report["status"] in {"done", "needs_review", "failed"}:
        for required_check in required_checks:
            if not command_satisfies(required_check, report["commands_run"]):
                errors.append(f"Required check missing from commands_run: {required_check}")

    if packet["verification_scope"] == "capsule_local":
        disallowed_repo_checks = {
            "./gradlew check build",
            "./gradlew build",
            "./gradlew check",
            "tools/scripts/update_todo_index.sh",
            "python3 tools/scripts/update_module_manifest.py",
        }
        for command in report["commands_run"]:
            if command in disallowed_repo_checks:
                errors.append(
                    "Capsule-local task ran repo-integration command outside delegated verification scope: "
                    f"{command}"
                )

    if packet["role"] == "verifier":
        if normalized_touched:
            errors.append("Verifier tasks must not touch implementation files; files_touched must be empty.")
        if not packet.get("verification_targets"):
            errors.append("Verifier task packet must declare verification_targets.")
        if report["status"] == "done" and packet.get("gotcha_review_required") and not report.get("gotchas_checked"):
            errors.append("Verifier report must list gotchas_checked when gotcha_review_required is true.")

    if report["status"] == "blocked" and report["blocker_category"] == "none":
        errors.append("Blocked report must set blocker_category to a non-'none' value.")
    if report["status"] == "needs_contract" and report["blocker_category"] != "contract":
        errors.append("needs_contract report must use blocker_category 'contract'.")
    if report["status"] == "done" and report["blocker_category"] != "none":
        errors.append("done report must use blocker_category 'none'.")

    if report["status"] == "done" and report["blockers"]:
        errors.append("Report status is 'done' but blockers is not empty.")
    if report["status"] in {"blocked", "needs_contract", "failed"} and not report["blockers"]:
        errors.append(f"Report status is '{report['status']}' but blockers is empty.")

    history = load_report_history(repo_root, history_dir, packet["task_id"], report_path)
    attempt_count = len(history) + 1
    if attempt_count > packet["max_iterations"]:
        errors.append(
            f"Task {packet['task_id']} exceeded max_iterations: {attempt_count} > {packet['max_iterations']}"
        )

    if history:
        _, previous = history[-1]
        previous_touched = {normalize_repo_path(repo_root, path) for path in previous["files_touched"]}
        current_touched = set(normalized_touched)
        previous_blockers = tuple(previous["blockers"])
        current_blockers = tuple(report["blockers"])

        if previous["summary"] == report["summary"]:
            errors.append("Loop brake triggered: report summary repeated without new progress.")
        if previous_blockers and previous_blockers == current_blockers:
            errors.append("Loop brake triggered: blocker set repeated without a new proposed action.")
        if previous_touched == current_touched and report["status"] != "done":
            errors.append("Loop brake triggered: touched file set repeated without completion.")

    if check_git:
        actual_changed = {
            path for path in git_changed_files(repo_root)
            if any(path_is_within(repo_root, path, allowed) for allowed in normalized_allowed)
        }
        reported_changed = set(normalized_touched)
        if actual_changed != reported_changed:
            errors.append(
                "files_touched does not match actual git changes within allowed_paths: "
                f"reported={sorted(reported_changed)}, actual={sorted(actual_changed)}"
            )

    return errors


def main():
    parser = argparse.ArgumentParser(
        description="Validate task-packet/report coherence and orchestration guardrails."
    )
    parser.add_argument("task_packet", help="Path to the task packet JSON file")
    parser.add_argument("--report", help="Path to the final report JSON file")
    parser.add_argument(
        "--active-packets-dir",
        help="Directory containing other active task packet JSON files for overlap checks",
    )
    parser.add_argument(
        "--history-dir",
        help="Directory containing prior agent-report JSON files for loop-brake checks",
    )
    parser.add_argument(
        "--check-git",
        action="store_true",
        help="Compare report.files_touched to actual git changes within allowed_paths",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    packet_path = (repo_root / args.task_packet).resolve() if not Path(args.task_packet).is_absolute() else Path(args.task_packet).resolve()

    try:
        packet = load_task_packet(repo_root, packet_path)
    except SchemaValidationError as exc:
        raise SystemExit(str(exc))

    active_packets_dir = None
    if args.active_packets_dir:
        active_packets_dir = (
            (repo_root / args.active_packets_dir).resolve()
            if not Path(args.active_packets_dir).is_absolute()
            else Path(args.active_packets_dir).resolve()
        )

    errors = validate_overlap(repo_root, packet, packet_path, active_packets_dir)

    if args.report:
        report_path = (repo_root / args.report).resolve() if not Path(args.report).is_absolute() else Path(args.report).resolve()
        history_dir = None
        if args.history_dir:
            history_dir = (
                (repo_root / args.history_dir).resolve()
                if not Path(args.history_dir).is_absolute()
                else Path(args.history_dir).resolve()
            )
        try:
            report = load_agent_report(repo_root, report_path)
        except SchemaValidationError as exc:
            raise SystemExit(str(exc))
        errors.extend(
            validate_report(
                repo_root=repo_root,
                packet=packet,
                report=report,
                history_dir=history_dir,
                report_path=report_path,
                check_git=args.check_git,
            )
        )

    if errors:
        raise SystemExit("\n".join(errors))

    print("Verified: Orchestration packet/report state is coherent.")


if __name__ == "__main__":
    main()
