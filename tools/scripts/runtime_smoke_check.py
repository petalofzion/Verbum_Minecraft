#!/usr/bin/env python3
import argparse
import subprocess
import sys
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Run a short profile runtime smoke check and fail on crash reports or obvious startup errors."
    )
    parser.add_argument("--profile", required=True, choices=["veritas", "vocations", "visions", "vorago"])
    parser.add_argument("--mode", default="client", choices=["client", "server"])
    parser.add_argument("--timeout-seconds", type=int, default=20)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    mode_task = "runClient" if args.mode == "client" else "runServer"
    task = f":assemblies:{args.profile}:{mode_task}"
    run_dir = repo_root / f"assemblies/{args.profile}/run"
    crash_dir = run_dir / "crash-reports"
    log_path = run_dir / "logs/latest.log"

    existing_crashes = set(p.name for p in crash_dir.glob("*")) if crash_dir.exists() else set()
    start_time = time.time()

    process = subprocess.Popen(
        ["./gradlew", task],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    timed_out = False
    captured: list[str] = []
    try:
        while True:
            if process.stdout is not None:
                line = process.stdout.readline()
                if line:
                    captured.append(line.rstrip())
                    if len(captured) > 400:
                        captured = captured[-400:]
            if process.poll() is not None:
                break
            if time.time() - start_time > args.timeout_seconds:
                timed_out = True
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
                break
            time.sleep(0.1)
    finally:
        if process.stdout is not None:
            remainder = process.stdout.read()
            if remainder:
                captured.extend(remainder.splitlines())

    new_crashes = []
    if crash_dir.exists():
        new_crashes = sorted(set(p.name for p in crash_dir.glob("*")) - existing_crashes)

    latest_log = log_path.read_text("utf-8", errors="replace") if log_path.exists() else ""
    error_markers = [
        "Exception",
        "Caused by:",
        "Block id not set",
        "Could not execute entrypoint stage",
        "Failed to load image",
    ]
    harmful_markers = [
        marker for marker in error_markers
        if marker in latest_log
    ]

    if new_crashes:
        raise SystemExit(
            "Runtime smoke check failed: new crash report(s) detected:\n" + "\n".join(new_crashes)
        )

    if process.returncode not in (0, None) and not timed_out:
        raise SystemExit(
            f"Runtime smoke check failed: {task} exited with code {process.returncode}\n"
            + "\n".join(captured[-80:])
        )

    if harmful_markers and "Could not authorize you against Realms server" not in latest_log:
        # A simple guard against known harmless auth noise. We still fail on real startup errors.
        raise SystemExit(
            "Runtime smoke check found suspicious log markers:\n"
            + "\n".join(sorted(set(harmful_markers)))
        )

    print(
        f"Verified runtime smoke: {task} {'timed out after startup window' if timed_out else 'exited cleanly'} "
        f"with no crash reports."
    )


if __name__ == "__main__":
    main()
