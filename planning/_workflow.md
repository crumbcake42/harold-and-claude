# Session Workflow

This file owns the session-resumption protocol for `sca-tracker`. `CLAUDE.md` triggers it on any "resume work" phrase. Read in full before responding; do not skip cases.

## File contract

**Holds:** Session-resumption protocol — case detection logic, sub-protocols for Cases 1/2/3, ambiguous-handoff paths, and the `_file-rules.md` regeneration procedure.
**Update when:** Workflow rules change (user explicitly requests an update); deferred sections are resolved in follow-up sessions.

---

## Vocabulary

Three-level hierarchy — enforce these terms; correct drift immediately before proceeding.

| Term | Definition |
|---|---|
| **Phase** | A named stage of the project (e.g., Conceptualization, Implementation). Contains multiple steps. |
| **Step** | A unit of deliberate work within a phase; may span multiple sessions if it doesn't fit one context window. Entries in `planning/sessions.md` are steps. (File rename from "sessions" to "steps" is pending.) |
| **Session** | One Claude Code context window. The atomic execution unit. A step maps to one session (Case 3) or is partitioned into multiple sessions (Case 2). |

---

## Entry protocol

On any "resume work" / "start the next session" / "vamos" / "yallah" / similar phrase:

1. Read `planning/handoff.md`.
2. Apply case detection below.
3. Follow the matching case protocol.

---

## Case detection

Inspect `handoff.md` → **Next session** section.

| Condition | Case |
|---|---|
| No "Next session" listed, or it references a new phase with no step list | Case 1 |
| "Next session" references a step with no scoped prompt | Case 2 |
| "Next session" references a step with a scoped prompt | Case 3 |
| Cannot determine | Ambiguous handoff |

---

## Case 1 — New major phase

*Trigger: entering a phase with no step list yet.*

1. State the phase goal in one sentence.
2. Surface the key decisions and tradeoffs on the table (use STOP-AND-CONFIRM gate vocabulary from `handoff.md`).
3. Discuss — do not propose a step list until the user signals readiness.
4. On consensus: draft the step list; confirm before writing to `planning/sessions.md`.

> **Deferred:** Phase-roster structure (where phases are enumerated and what triggers a phase change) — to be resolved in a follow-up session. Until then, infer phase transitions from `handoff.md`'s "Current phase" field.

---

## Case 2 — New step

*Trigger: next session pointer references a step with no scoped prompt.*

1. Read the step brief in `planning/sessions.md`.
2. Assess: does the step fit one session (one Claude Code context window)?
   - Signals it **doesn't** fit: more than two coupled decisions; requires writing multiple new files from scratch; expected duration >60 min.
   - *(Detailed heuristics deferred — follow-up session.)*
3. If it fits → fall through to Case 3 immediately.
4. If it doesn't fit:
   a. Surface partitioning options with tradeoffs; discuss.
   b. On consensus: write revised step entries to `planning/sessions.md`; update `handoff.md` next-session pointer.
   c. Fall through to Case 3 for the first sub-step.

---

## Case 3 — Scoped session

*Trigger: next session pointer references a step with a scoped prompt.*

1. Read `handoff.md` → **Prompt for the next session** and **Open questions**.
2. Read `planning/decisions.md` and any input files listed in the step brief in `planning/sessions.md`.
3. Enter planning mode: draft a session plan in chat; wait for explicit approval (STOP-AND-CONFIRM gate in `handoff.md` applies). Do not touch files until approved.
4. Implement.
5. When all scope items are done: notify the user and wait for an explicit wrap-up signal ("wrap up," "session complete," or similar) before updating any files.
6. On wrap-up signal: run the **completion protocol** below. Use the same protocol on interruption (incomplete scope) — the update still runs; note the incomplete items in the Last session summary.

### Completion protocol

a. **`planning/handoff.md`** — move Next session → Last session summary; advance Next session pointer to the following step in `sessions.md`; refresh Open questions; rewrite Prompt for the next session.
b. **`planning/decisions.md`** — append ADR entries for any decisions finalized in the session.
c. **Other files** — consult `planning/_file-rules.md` to identify any other files that need updating based on work done.
d. **`planning/_file-rules.md`** — regenerate if any planning file's `## File contract` block changed during the session. See regeneration procedure below.

---

## Ambiguous handoff

*Trigger: cannot determine which case applies from `handoff.md`.*

Ask the user: "The handoff doesn't clearly indicate where we left off. Can you tell me where to pick up, or should I figure it out?"

### Path A — User explains where to pick up

1. Map the stated pickup point to:
   - A file/section in `planning/` (use section-heading anchors).
   - A step in `planning/sessions.md`.
2. Both exist and the step is within the current phase scope → accept; proceed to Case 2 or Case 3 as appropriate.
3. Either is missing, or the step is outside any scoped plan → warn; list the specific mismatches; ask the user to confirm or amend before proceeding.

### Path B — User asks the agent to figure it out

1. Read all files in `planning/`.
2. Check `git log` for recent changes to planning files.
3. Compare the declared **Next session** in `handoff.md` against the codebase (are expected outputs of prior steps present?).
4. Surface: what the plans say is next; what the codebase reflects; any drift between them.
5. Propose a pickup point; confirm with the user before proceeding.
6. If `_file-rules.md` appears stale, regenerate it as part of this check (see below).

> **Deferred:** Drift signal taxonomy (what counts as drift, how to surface it) — follow-up session.

---

## `_file-rules.md` regeneration procedure

`planning/_file-rules.md` is a generated index. Do not edit it manually.

**To regenerate:**
1. Read every `planning/*.md` file (excluding `_file-rules.md` itself).
2. Find the `## File contract` section in each file.
3. Compile all contract blocks into `_file-rules.md` under the filename as a heading.
4. Update the "Last regenerated" date.

Regeneration does not require user approval — it is a mechanical read-and-compile with no design decisions.

**Trigger regeneration when:**
- A session adds or modifies a planning file's `## File contract` block.
- Path B detects the registry is stale (a file exists without a matching entry in the registry, or vice versa).
- The user requests it explicitly.
