# Backend directory structure — rewind point

Generated 2026-05-19 at user request. Documents the hexagonal `app/` layout commitment and the rewind tag pointing at the pre-build-out state, so this choice can be revisited if it ages badly.

> **SUPERSEDED 2026-05-20 (Session 41) by ADR-0070.** Step 2.2b-A re-examined the backend topology with FastAPI committed and the command engine built, and replaced the hexagonal horizontal layout described below with **vertical feature slices over a shared `framework/` engine** (`framework/` + `adapters/` + `auth/` + `features/<entity>/`). The reasoning and the new structure are in ADR-0070. This document is retained for trace continuity; the layout, alternatives, and revisit criteria below describe the superseded decision. The rewind tag `rewind/2026-05-19-hexagonal-commit` still exists but no longer marks an active commitment.

---

## The decision

**Backend `app/` keeps the hexagonal / ports-and-adapters layout** as it stands on disk after M0.3:

```
backend/app/
├── framework/   # engine — capture, command, db, dispatcher, exceptions, history, locks
├── domain/     # entity declarations (currently empty; M1+ populates)
├── adapters/   # concrete I/O (currently empty)
├── routes/     # HTTP layer (currently: healthcheck)
├── config.py
└── main.py
```

Cross-cutting domain modules (`domain/blockers/` for the closure-gate registry, future `domain/notifications/` etc.) sit as peers of entity folders inside `domain/`. Cascade content lives in the originating entity's folder (e.g., the cascade-keep-FK declaration goes in `domain/wa_codes/`).

## Alternatives weighed and rejected

1. **Flat-per-feature** (Django/Flask style — `app/schools/`, `app/projects/`, … with `app/common/` for shared utilities). Strong for thin entities and feature-level locality but conflates engine code with feature code at top level and gives cross-cutting modules (blockers, future cascades, future notifications) no natural home — they'd compete with entities at the same depth.
2. **Flat-with-`framework/`-as-sibling** (a hybrid: drop `domain/` parent, keep `framework/` as a top-level peer to entity folders). Lighter nesting but at ~21 entities + multiple cross-cutting modules, `app/` becomes 25+ folders deep at top level — visual scan cost dominates the benefit. Also creates a vocabulary gap with planning docs that use "framework" / "domain" as paired terms.

## Why hexagonal landed (~70/30 confidence)

- **Scale**: 21 entities + cross-cutting modules makes hexagonal's narrower top-level worth the extra path depth.
- **Vocabulary alignment**: `framework.md` / `domain-model.md` and "framework-enforced" terminology map directly to the folder split.
- **Engine-first design history**: Steps 1–5 built the framework as a deliberate reusable substrate; foregrounding it as one folder reflects that investment.
- **Cross-cutting modules get a home**: `domain/blockers/` as a peer to entity folders inside `domain/` reads naturally; in flat layouts it competes with entities at top level.

The 30%-case for flat: if framework code never gets read as a unit in practice and `framework/` is just a bucket for dispatcher / history files, the `domain/` parent stops doing work. That's "wait and see," not "know now."

## Rewind anchor

- **Tag**: `rewind/2026-05-19-hexagonal-commit`
- **Commit**: `18e0fca` (M0.3 / Step 1.3b complete: history infrastructure + real capture sink)
- **Branch at tag time**: `m0/03-dispatcher-and-history`
- **State**: `domain/` and `adapters/` are empty; only `framework/` and `routes/` carry code. **The cheapest possible moment to pivot is now** — any pivot done after M1 lands carries proportionally more refactoring cost.

To inspect the state at decision time: `git show rewind/2026-05-19-hexagonal-commit` or `git checkout rewind/2026-05-19-hexagonal-commit`.

## Revisit criteria

Pull on the rewind tag if any of the following surface during M1–M3 build-out:

1. **`framework/` never needs to be read as a unit.** If reading the engine holistically isn't something that ever happens — i.e., people only ever open one file in `framework/` at a time — the `domain/` parent stops earning its visual-layering job and the extra path depth becomes pure noise.
2. **Cross-entity command placement decisions stay genuinely ambiguous after 5+ landings.** If compound commands like `create_project`, `issue_wa`, `approve_rfa` keep generating "where does this go?" deliberation rather than landing in obvious homes, the layering may not be matching how the code actually wants to be organized.
3. **Imports from `app.domain.*` dominate test setup to the point of friction.** Path-depth tax on tests is the most visible cost of the extra nesting; if it noticeably slows fixture authoring, that's a signal.
4. **Folder pattern proliferation inside entities.** If entity folders sprout parallel sub-conventions (`commands/`, `cascades/`, `derivations/`, `invariants/`, `blockers/`, …) and the conventions drift inconsistently across entities, the hexagonal split may be too coarse — flat-per-feature plus per-feature internal organization may serve better.

## Pointers

- **Session of decision**: Session 32 (2026-05-19), pre-M1 build-out.
- **Conversation**: backend directory structure deliberation; covered hexagonal vs. flat vs. hybrid + cross-cutting module placement (blockers, closures, cascades).
- **Related ADRs**: none filed — directory structure is implementation-phase work and below the threshold for an ADR. Tagged + this follow-up are the durable record.
- **Memory updated**: `feedback_recommendation_strength.md` — recurrence of agreeableness-drift pattern noted under a new trigger (user-stated preference, not contra prompt).
