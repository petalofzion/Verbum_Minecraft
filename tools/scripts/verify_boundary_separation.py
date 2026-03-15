#!/usr/bin/env python3
import argparse
import re
from pathlib import Path


FORBIDDEN_PLATFORM_IMPORT = re.compile(r"^import\s+(net\.minecraft|net\.fabricmc|com\.mojang)\.", re.MULTILINE)
FORBIDDEN_ASSEMBLY_IMPORT = re.compile(r"^import\s+com\.verbum_minecraft\.(veritas|vocations|visions|vorago)\.", re.MULTILINE)
FORBIDDEN_FEATURE_IMPORT = re.compile(r"^import\s+com\.verbum_minecraft\.features\.", re.MULTILINE)
SUSPICIOUS_API_SELECTOR = re.compile(r"\bString\s+\w*(HandlerClass|ClassName|ImplementationClass)\b")


def java_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(root.rglob("*.java"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def rel(path: Path, repo_root: Path) -> str:
    return str(path.relative_to(repo_root))


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify core architectural separation boundaries.")
    parser.add_argument(
        "--repo-root",
        default=Path(__file__).resolve().parents[2],
        type=Path,
        help="Repository root. Defaults to the script's repo root.",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    findings: list[str] = []

    pure_roots = [
        repo_root / "modules/core/api",
        repo_root / "modules/core/spi",
        repo_root / "modules/features",
    ]
    for root in pure_roots:
        for path in java_files(root):
            text = read_text(path)
            if FORBIDDEN_PLATFORM_IMPORT.search(text):
                findings.append(f"{rel(path, repo_root)} imports Minecraft/Fabric classes in a pure module path.")
            if root.name != "features" and FORBIDDEN_ASSEMBLY_IMPORT.search(text):
                findings.append(f"{rel(path, repo_root)} imports an assembly package from a pure module path.")

    feature_root = repo_root / "modules/features"
    for path in java_files(feature_root):
        text = read_text(path)
        if FORBIDDEN_ASSEMBLY_IMPORT.search(text):
            findings.append(f"{rel(path, repo_root)} imports an assembly package from a feature capsule.")
        if FORBIDDEN_FEATURE_IMPORT.search(text):
            package_match = re.search(r"^package\s+([a-zA-Z0-9_.]+);", text, re.MULTILINE)
            imports = FORBIDDEN_FEATURE_IMPORT.findall(text)
            if imports:
                findings.append(f"{rel(path, repo_root)} imports another feature package directly.")

    api_root = repo_root / "modules/core/api/src/main/java"
    for path in java_files(api_root):
        text = read_text(path)
        if SUSPICIOUS_API_SELECTOR.search(text):
            findings.append(f"{rel(path, repo_root)} exposes class-name based implementation selectors in core API.")

    if findings:
        print("Boundary separation check failed:")
        for finding in findings:
            print(f"- {finding}")
        raise SystemExit(1)

    print("Boundary separation check passed.")


if __name__ == "__main__":
    main()
