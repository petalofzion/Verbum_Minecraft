# Rule of Ashes Capsule

## Purpose
This capsule adds a Vorago profile manual item, `Rule of Ashes`, as a library-backed book. It frames Vorago as Visions under harsher laws: pressure, scarcity, risk, and discipline.

## Scope
- Library-backed manual registration via `FeatureEntrypoint`
- Packaged player-facing book text for the Vorago edition
- Pure data and logic only (no Minecraft/Fabric classes)

## Dependencies
- `modules/core/api`
- `modules/core/spi`

## Key Files
- `module.json`
- `src/main/java/.../RuleOfAshesFeature.java`
- `src/main/resources/META-INF/services/com.verbum_minecraft.spi.FeatureEntrypoint`
- `docs/PRD.md`, `docs/MVP.md`, `docs/TODO.md`
- `docs/agent-logs/`

## Asset Checklist (Item)
- `src/main/resources/assets/verbum/items/rule_of_ashes.json`
- `src/main/resources/assets/verbum/models/item/rule_of_ashes.json`
- `src/main/resources/assets/verbum/textures/item/rule_of_ashes.png`
- `src/main/resources/assets/verbum/lang/en_us.json`

## Asset Checklist (Library Book)
- `src/main/resources/assets/verbum/books/rule_of_ashes@vorago.txt`
