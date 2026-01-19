# New Capsule Checklist (Repo Agent)

## 1) Create Capsule Skeleton
- [ ] Create `modules/features/<domain>/<feature>/`
- [ ] Copy templates from `docs/templates/capsule/`
- [ ] Ensure `module.json` values are unique and correct
- [ ] Add SPI file under `src/main/resources/META-INF/services/`

## 2) Author Capsule Docs
- [ ] Fill in `README.md`
- [ ] Fill in `docs/PRD.md`
- [ ] Fill in `docs/MVP.md`
- [ ] Fill in `docs/TODO.md`
- [ ] Keep `docs/agent-logs/README.md` in place

## 3) Guardrails
- [ ] Add capsule `AGENTS.md`
- [ ] Confirm no cross-feature imports
- [ ] Confirm no Minecraft/Fabric classes in capsule

## 4) Wiring (Assembly)
- [ ] Ensure assembly dependencies include the capsule module
- [ ] Ensure ServiceLoader registration is correct

## 5) Tests
- [ ] `./gradlew build`
- [ ] `./gradlew check`

## 6) Index
- [ ] Run `tools/scripts/update_todo_index.sh`
