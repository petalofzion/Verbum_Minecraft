# Update Surfaces

This is the repo's central obligations list for "what else must be updated when X changes."

Use it as a procedural checklist, not as a narrative guide.

## Rules
- Prefer generated surfaces over hand-edited mirrors.
- Repo agents own repo-wide refreshes unless a task packet explicitly delegates `repo_integration`.
- When in doubt, refresh the generated indexes and run `./gradlew check build`.

## Obligations Matrix
| Change Type | Must Inspect | Must Update If Changed | Verify With | Capsule Agent Allowed? | Escalate When |
| --- | --- | --- | --- | --- | --- |
| New capsule/module | `module.json`, capsule docs, SPI registration | `modules/modules.toml`, `docs/CAPSULE_INDEX.*`, `docs/TODO_INDEX.md` | `python3 tools/scripts/update_module_manifest.py`, `python3 tools/scripts/update_capsule_index.py`, `tools/scripts/update_todo_index.sh`, `./gradlew check build` | Capsule can create local files; repo agent owns indexes | new contract or assembly wiring needed |
| Changed module metadata | `module.json`, profile placement | `modules/modules.toml`, `docs/CAPSULE_INDEX.*`, profile docs if semantics changed | `python3 tools/scripts/update_module_manifest.py`, `python3 tools/scripts/update_capsule_index.py`, `./gradlew check build` | no, unless packet includes repo integration | metadata changes alter profile identity or inheritance |
| New API/SPI contract | `modules/core/api`, `modules/core/spi`, `docs/contracts/CORE_API.md` | `docs/contracts/contract_wiring.tsv`, `docs/contracts/CONTRACT_INDEX.md`, possibly ADRs | `tools/scripts/update_contract_index.sh`, `./gradlew check build` | no | contract shape affects multiple capsules or public API |
| Changed contract wiring | assembly wiring and registrar code | `docs/contracts/contract_wiring.tsv`, `docs/contracts/CONTRACT_INDEX.md`, wiring docs | `tools/scripts/update_contract_index.sh`, `./gradlew check build` | no | change touches assemblies or multiple profiles |
| Assembly wiring change | `assemblies/*`, `docs/wiring/ASSEMBLY_WIRING.md`, `docs/wiring/UI_WIRING.md` | relevant wiring docs, `docs/contracts/contract_wiring.tsv` if contract consumption changes | `tools/scripts/update_contract_index.sh`, `./gradlew check build` | no | any Fabric/Minecraft/config/IO change |
| Player-facing content/manual change | profile docs, style bible, capsule README/PRD | capsule docs, `docs/CAPSULE_INDEX.*` if purpose/scope changed | `python3 tools/scripts/update_capsule_index.py`, `./gradlew check build` | yes, inside capsule | copy change alters profile semantics or naming |
| Library-backed book change | `LibraryBookDef` book id, asset path, lang/item/model files | matching `assets/<ns>/books/<path>@<edition>.txt` when edition-qualified | `./gradlew verifyLibraryBookResources`, `./gradlew check build` | yes, if local to the capsule | resource naming no longer matches declared book id |
| Orchestration schema/tooling change | task/report schemas, wrapper scripts, quickstart docs | examples, `docs/agents/*`, `tools/scripts/*` | `./gradlew verifyAgentProtocolAssets`, `./gradlew check build` | no | change affects packet/report contract or executor behavior |
| New gotcha / version pitfall | version-specific behavior | `docs/GOTCHAS.md` | manual review + `./gradlew check build` | yes, if local discovery; repo agent should integrate | issue affects assemblies, assets, or multiple capsules |
| New subsystem / architecture shift | architecture map, runtime constitution, ADR rules | ADR, relevant core docs, possibly update surfaces | `./gradlew check build` plus any benchmark obligations | no | architecture or public contract changes |

## Generated Surfaces
Refresh these through scripts, not by hand:
- `modules/modules.toml` via `python3 tools/scripts/update_module_manifest.py`
- `docs/CAPSULE_INDEX.md` and `docs/CAPSULE_INDEX.tsv` via `python3 tools/scripts/update_capsule_index.py`
- `docs/TODO_INDEX.md` via `tools/scripts/update_todo_index.sh`
- `docs/contracts/CONTRACT_INDEX.md` via `tools/scripts/update_contract_index.sh`

## Minimum Repo-Agent Finish Sequence
```bash
python3 tools/scripts/update_module_manifest.py
python3 tools/scripts/update_capsule_index.py
tools/scripts/update_todo_index.sh
tools/scripts/update_contract_index.sh   # when contracts/wiring changed
./gradlew check build
```
