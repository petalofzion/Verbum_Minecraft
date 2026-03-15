# Capsule TODO: Bible Feature

This file tracks **capsule-local** work only. It is maintained by capsule agents.

## How to Use
- Add tasks you discover while implementing.
- Keep scope limited to this capsule.
- Mark items done with `[x]` and keep ordering stable.
- If you identify cross-module work (API/SPI/assemblies), log it in `docs/agent-logs/` and stop.

## Tasks
- [ ] Verify Bible item appears in creative inventory (creative tab wiring implemented; runtime verification pending).
- [ ] Verify Bible reads the full text offline via the library-backed reader.
- [x] Register Bible as a library-backed book via `LibraryBookDef`.
- [x] Add full Bible content asset (Douay-Rheims) to `assets/verbum/books/bible.txt`.
