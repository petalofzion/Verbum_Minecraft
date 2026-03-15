#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


PROFILE_LADDER = ["veritas", "vocations", "visions", "vorago"]
EDITION_TO_PROFILES = {
    "shared": PROFILE_LADDER,
    "veritas": PROFILE_LADDER,
    "vocations": PROFILE_LADDER[1:],
    "visions": PROFILE_LADDER[2:],
    "vorago": PROFILE_LADDER[3:],
}

CONTRACT_IMPORT_RE = re.compile(r"^\s*import\s+(com\.verbum_minecraft\.(?:api|spi)\.[A-Za-z0-9_.]+);", re.MULTILINE)
PACKAGE_RE = re.compile(r"^\s*package\s+([a-zA-Z0-9_.]+);", re.MULTILINE)
DECL_RE = re.compile(r"public\s+(?:class|interface|enum|record)\s+([A-Za-z0-9_]+)")


def derive_display_name(module_dir: Path) -> str:
    return module_dir.name.replace("-", " ").title()


def first_readme_summary(readme_path: Path) -> str:
    if not readme_path.exists():
        return ""
    lines = readme_path.read_text(encoding="utf-8").splitlines()
    paragraph = []
    in_frontmatter = False
    for raw in lines:
        line = raw.strip()
        if line == "---" and not paragraph:
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter:
            continue
        if not line:
            if paragraph:
                break
            continue
        if line.startswith("#"):
            continue
        if line.startswith(">"):
            continue
        paragraph.append(line)
    return " ".join(paragraph).strip()


def java_declared_types(java_path: Path):
    if not java_path.exists():
        return []
    text = java_path.read_text(encoding="utf-8")
    package_match = PACKAGE_RE.search(text)
    package_name = package_match.group(1) if package_match else None
    if not package_name:
        return []
    return [f"{package_name}.{match.group(1)}" for match in DECL_RE.finditer(text)]


def scan_contract_usage(module_dir: Path):
    contract_imports = set()
    entrypoints = []
    for java_path in sorted((module_dir / "src/main/java").rglob("*.java")) if (module_dir / "src/main/java").exists() else []:
        text = java_path.read_text(encoding="utf-8")
        contract_imports.update(match.group(1) for match in CONTRACT_IMPORT_RE.finditer(text))
        entrypoints.extend(java_declared_types(java_path))
    return sorted(contract_imports), sorted(entrypoints)


def docs_present(module_dir: Path) -> str:
    required = [
        module_dir / "README.md",
        module_dir / "docs/PRD.md",
        module_dir / "docs/MVP.md",
        module_dir / "docs/TODO.md",
    ]
    if all(path.exists() for path in required):
        return "yes"
    if any(path.exists() for path in required):
        return "partial"
    return "no"


def tests_present(module_dir: Path) -> str:
    has_unit = (module_dir / "src/test/java").exists()
    has_game = (module_dir / "src/gametest/java").exists()
    if has_unit and has_game:
        return "unit+gametest"
    if has_unit:
        return "unit"
    if has_game:
        return "gametest"
    return "none"


def module_kind(project_key: str) -> str:
    if project_key.startswith("modules/features/"):
        return "capsule"
    if project_key.startswith("modules/core/"):
        return "core"
    if project_key.startswith("modules/world/"):
        return "world"
    if project_key.startswith("modules/magic/"):
        return "magic"
    if project_key.startswith("modules/tech/"):
        return "tech"
    return "module"


def scan_modules(repo_root: Path):
    records = []
    for metadata_path in sorted(repo_root.glob("modules/**/module.json")):
        module_dir = metadata_path.parent
        if not (module_dir / "build.gradle").exists() and not (module_dir / "build.gradle.kts").exists():
            continue

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        edition = str(metadata["edition"])
        if edition not in EDITION_TO_PROFILES:
            raise SystemExit(f"Unsupported edition '{edition}' in {metadata_path}")

        project_key = module_dir.relative_to(repo_root).as_posix()
        contract_imports, declared_types = scan_contract_usage(module_dir)
        summary = first_readme_summary(module_dir / "README.md")
        entrypoint = str(metadata.get("entrypointClass", "")).strip()

        records.append(
            {
                "project_key": project_key,
                "kind": module_kind(project_key),
                "module_id": str(metadata["id"]),
                "name": derive_display_name(module_dir),
                "domain": str(metadata["domain"]),
                "edition": edition,
                "profiles": ",".join(EDITION_TO_PROFILES[edition]),
                "provides_feature": "yes" if metadata.get("providesFeature") else "no",
                "entrypoint_class": entrypoint or "-",
                "declared_types": ",".join(declared_types) if declared_types else "-",
                "depends_on": ",".join(metadata.get("dependsOn", [])) if metadata.get("dependsOn") else "-",
                "contracts_used": ",".join(contract_imports) if contract_imports else "-",
                "docs": docs_present(module_dir),
                "tests": tests_present(module_dir),
                "purpose": summary or "-",
            }
        )
    return records


def format_tsv(records):
    headers = [
        "project_key",
        "kind",
        "module_id",
        "name",
        "domain",
        "edition",
        "profiles",
        "provides_feature",
        "entrypoint_class",
        "declared_types",
        "depends_on",
        "contracts_used",
        "docs",
        "tests",
        "purpose",
    ]
    lines = ["\t".join(headers)]
    for record in records:
        lines.append("\t".join(record[h].replace("\t", " ").replace("\n", " ") for h in headers))
    return "\n".join(lines) + "\n"


def format_md(records):
    lines = [
        "# Capsule Index",
        "",
        "This file is auto-generated by `tools/scripts/update_capsule_index.py`.",
        "Do not edit by hand.",
        "",
        "This index is the fastest repo-wide inventory for what modules/capsules exist, what tier they belong to,",
        "what contracts they use, and what profile ladder they ship in.",
        "",
        "## Inventory",
        "",
        "| Project | Kind | Module ID | Domain | Edition | Profiles | Feature | Depends On | Contracts Used | Docs | Tests | Purpose |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for record in records:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{record['project_key']}`",
                    record["kind"],
                    f"`{record['module_id']}`",
                    record["domain"],
                    f"`{record['edition']}`",
                    f"`{record['profiles']}`",
                    record["provides_feature"],
                    f"`{record['depends_on']}`",
                    f"`{record['contracts_used']}`",
                    record["docs"],
                    record["tests"],
                    record["purpose"].replace("|", "\\|"),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- `Kind` distinguishes feature capsules from support modules so repo agents can see whether a unit is player-facing content or infrastructure.",
            "- `Profiles` is derived from the edition ladder: `veritas -> vocations -> visions -> vorago`.",
            "- `Contracts Used` is scanned from Java imports under `com.verbum_minecraft.api.*` and `com.verbum_minecraft.spi.*`.",
            "- Use `docs/UPDATE_SURFACES.md` for what else must be refreshed when this inventory changes.",
        ]
    )
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Generate or verify docs/CAPSULE_INDEX.* from module metadata.")
    parser.add_argument("--check", action="store_true", help="Verify generated capsule index files are up to date")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    records = scan_modules(repo_root)
    tsv_output = format_tsv(records)
    md_output = format_md(records)

    tsv_path = repo_root / "docs/CAPSULE_INDEX.tsv"
    md_path = repo_root / "docs/CAPSULE_INDEX.md"

    if args.check:
        if not tsv_path.exists() or not md_path.exists():
            raise SystemExit("Missing capsule index outputs. Run tools/scripts/update_capsule_index.py")
        if tsv_path.read_text(encoding="utf-8") != tsv_output or md_path.read_text(encoding="utf-8") != md_output:
            raise SystemExit("Capsule index is out of date. Run tools/scripts/update_capsule_index.py")
        return

    tsv_path.write_text(tsv_output, encoding="utf-8")
    md_path.write_text(md_output, encoding="utf-8")


if __name__ == "__main__":
    main()
