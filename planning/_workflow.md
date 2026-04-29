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
| **Phase** | A named stage of the project (e.g., Conceptualization, Implementation). Contains multiple steps. Enumerated in `planning/phases.md`. |
| **Step** | A unit of deliberate work within a phase; may span multiple sessions if it doesn't fit one context window. Entries in `planning/steps.md` are steps. |
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
4. On consensus: draft the step list; confirm before writing to `planning/steps.md`.

### Phase roster protocol

Phases are enumerated in `planning/phases.md`. Each entry: name, one-line goal, status (current / complete / not started), pointer to step list.

**Phase-change trigger:** a dedicated ADR in `planning/decisions.md` (e.g., "Conceptualization phase complete; implementation begins"). When that ADR lands:
1. Update `phases.md` — mark current phase complete; mark next phase current.
2. Archive current step list to `planning/steps.archive/<phase-name>.md`.
3. Create new `planning/steps.md` for the new phase.
4. Update `handoff.md`'s "Current phase" line to point at the new phase.

**Lightweight gate:** announce the four writes in chat ("phase N complete, archiving steps and creating new steps.md — ok?"); wait for yes before writing. Not full deliberation.

**Initial enumeration:** just-in-time. `phases.md` holds current phase + next phase stub only. Do not pre-enumerate beyond the next phase. Add a new phase stub before the current one ends.

---

## Case 2 — New step

*Trigger: next session pointer references a step with no scoped prompt.*

1. Read the step brief in `planning/steps.md`.
2. Assess: does the step fit one session (one Claude Code context window)?

   Run the following checklist. **Any one signal fires = doesn't fit; split.** Name which signal(s) fired before proposing a partition.

   | # | Signal | Notes |
   |---|---|---|
   | 1 | More than one independently-deliberable decision | A coupled pair (ADRs reference each other) counts as one. Two unrelated decisions count as two. |
   | 2 | More than one new artifact requires drafting from scratch | "Artifact" = file *or* major top-level section. |
   | 3 | Duration estimate >60 min | Yellow at 45–60 min — consider scope-trimming before splitting. |
   | 4 | Required input reading exceeds ~3 substantial planning files or ~1000 LOC | Input alone eats context budget. |
   | 5 | Cross-concern reach | Step joins two distinct concern areas. Test: would the ADRs land in different topical clusters? Caveat: some apparent AND pairs are one concern (lifecycle + invariants are temporal — current Step 3 grouping is correct). |
   | 6 | Depends on outputs that don't yet exist | If inputs include "result of step X" and X is unscoped, push back on the brief before sizing. |
   | 7 | Iterative-discovery framing or unclear scope | "We'll figure out X as we go." Partition the discovery from the decision. |

   Not codified as signals: "complexity" / "uncertainty" — these collapse to (5)–(7) in practice.
3. If it fits → fall through to Case 3 immediately.
4. If it doesn't fit:
   a. Surface partitioning options with tradeoffs; discuss.
   b. On consensus: write revised step entries to `planning/steps.md`; update `handoff.md` next-session pointer.
   c. Fall through to Case 3 for the first sub-step.

---

## Case 3 — Scoped session

*Trigger: next session pointer references a step with a scoped prompt.*

1. Read `handoff.md` → **Prompt for the next session** and **Open questions**.
2. Read `planning/decisions.md` and any input files listed in the step brief in `planning/steps.md`.
3. Enter planning mode: draft a session plan in chat; wait for explicit approval (STOP-AND-CONFIRM gate in `handoff.md` applies). Do not touch files until approved.
4. Implement.
5. When all scope items are done: notify the user and wait for an explicit wrap-up signal ("wrap up," "session complete," or similar) before updating any files.
6. On wrap-up signal: run the **completion protocol** below. Use the same protocol on interruption (incomplete scope) — the update still runs; note the incomplete items in the Last session summary.

### Completion protocol

a. **`planning/handoff.md`** — move Next session → Last session summary; advance Next session pointer to the following step in `steps.md`; refresh Open questions; rewrite Prompt for the next session.
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
   - A step in `planning/steps.md`.
2. Both exist and the step is within the current phase scope → accept; proceed to Case 2 or Case 3 as appropriate.
3. Either is missing, or the step is outside any scoped plan → warn; list the specific mismatches; ask the user to confirm or amend before proceeding.

### Path B — User asks the agent to figure it out

1. Read all files in `planning/`.
2. Check `git log` for recent changes to planning files.
3. Compare the declared **Next session** in `handoff.md` against the codebase (are expected outputs of prior steps present?).
4. Surface: what the plans say is next; what the codebase reflects; drift between them (see drift protocol below).
5. Propose a pickup point; confirm with the user before proceeding.
6. If `_file-rules.md` appears stale, regenerate it as part of this check (see below).

### Drift detection protocol

Run checks (a), (b), (c) in order. Plan-internal drift is the dominant case; plan-vs-codebase drift is rare and more serious.

**Check (a) — Plan-internal: stale handoff pointer.** Compare `handoff.md`'s "Next session" against `steps.md`. If the referenced step's outputs already exist (declared artifact present *and* ADRs for that step landed in `decisions.md`), identify the next genuinely-incomplete step. **Lightweight gate:** state in chat — *"handoff is stale; next incomplete step is X — update?"* — and wait for yes/no. On yes, write the updated pointer to `handoff.md`. No full deliberation required.

**Check (b) — Plan-internal: cross-file inconsistencies.** Other plan-vs-plan mismatches not covered by (a): "Last session summary" in `handoff.md` disagrees with `steps.md` status; pointer integrity between planning files broken; vocabulary drift (e.g., "session" used where "step" is the agreed term). Surface as a categorized list — **Missing / Unexpected / Mismatched** — with one-line evidence per item. User resolves; agent does not act.

**Check (c) — Plan vs codebase.** For each artifact `steps.md` declares should exist, verify it exists and roughly matches the brief. Scan `git log` for commits to code or planning files not reflected in declared state. Classify each finding:
- **Coherent tack-on** — fits the plan envelope (e.g., new column on an existing model, signature change on a documented function). One-line note; record-or-ignore call belongs to the user.
- **Off-course** — drift the agent cannot resolve with safe assumptions. Brief summary + the assumptions that *would* be needed to resolve it. **Surface only — do not act on the assumptions.** STOP-AND-CONFIRM gate stands.

**Surfacing order.** Pickup-point proposal first (steps (a) resolution or proposal); drift findings second, tagged by check (a/b/c) and category.

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
