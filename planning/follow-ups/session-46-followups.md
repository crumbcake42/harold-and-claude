# Session 46 follow-ups — address at the start of the next session

Three items raised during Session 46 (Step 2.2c) via a `/eval-prompt` tangent.
Surface these at the next session head, before resuming step work. Items 2 and 3
are discussion items (deliberate, don't pre-decide).

**Status (Session 48).** Items 2, 3, 4 land in the `m1/admin-followups` dedicated
non-milestone slot — see `handoff.md` § Next session. Item 1 (container/
presentational split) is deferred into Step 2.2d-2's head deliberations and is
**not** part of the slot.

---

## 1. Refined design-question prompt — to be read and answered

A `/eval-prompt` audit refined a frontend design question (whether to adopt a
container/presentational component split). The refined prompt, to be answered as
a frontend-architecture deliberation:

```
Assess whether the frontend should adopt a container/presentational split — a
logic/state "container" component rendering a pure-display child — and, if
warranted, codify the result as an addition to `frontend/src/PATTERNS.md`.

Context (you have repo access — read rather than assume):
- Worked example: `src/pages/login/index.tsx`. The lean is to split `LoginPage`
  into a container holding the hooks and logic and a presentational child
  holding only the JSX. Treat this as illustrative; generalize the question to
  all frontend components, not just pages.
- The proposal resembles the established container/presentational (smart/dumb)
  pattern — use standard terminology, don't coin new names.
- Reconcile against the existing four-layer architecture in `PATTERNS.md` and
  ADR-0064/0066, which already separate page compositions from presentational
  feature components. State explicitly whether this proposal overlaps with,
  conflicts with, or refines that — `login` is itself atypical because its
  rendering is already delegated to `<LoginForm>`.

Do:
1. Enumerate the popular conventions for where the logic/display boundary falls
   — e.g. hooks only in the container; hooks + handlers; hooks + handlers +
   derived values; strict props-only child. Compare them on testability,
   churn/prop-drilling cost, and fit with a codebase where pages already
   delegate rendering to feature components.
2. For each boundary option, judge whether it warrants a strict rule — and if
   so the enforcement mechanism (ESLint, a `PATTERNS.md` clause, or review-time
   judgment) — or case-by-case application.
3. Recommend the option best suited to this codebase, with reasoning, and name
   when an exception is legitimate.
4. Argue the case against adopting any split, so the recommendation is auditable.

Output: prose analysis covering 1–4, then — only if the recommendation is to
adopt — a draft `PATTERNS.md` section. Assess objectively; do not bias toward
the stated lean.
```

Notes: not a roadmap step — a conventions deliberation. If the recommendation is
to adopt, the `PATTERNS.md` addition is likely ADR-worthy (flag at deliberation
head). Subject to the STOP-AND-CONFIRM gate.

---

## 2. Discuss — make `/eval-prompt` mid-session aware

`/eval-prompt` currently assumes the refined prompt targets a *fresh* session.
Used mid-session it is awkward and somewhat circular — refining a prompt for the
same session that already holds the context. Proposed change: a mid-session mode
that **forks into a meta conversation, refines only the prompt itself, and holds
it until the user explicitly approves it to be sent** (the skill does not act on
the prompt until approval). Discuss: mode flag vs. default behavior; how the
"fork" is bracketed; how approval re-enters the main task.

---

## 3. Discuss — add an `/assess` skill

Proposed new skill: takes an input proposal and returns a structured assessment
plus a final evaluation with a stated **confidence level**. Distinct from
`/eval-prompt` (which improves a prompt *before* sending) — `/assess` evaluates a
proposal under a forced-objective, agenda-free framing. Discuss: input shape,
output structure, the confidence scale, and whether it earns a skill vs. an
inline instruction.

---

## 4. Routing — confirm route paths before assuming; define the default path shape

**Process correction:** route / URL path structure is a gated structural
decision — confirm it before assuming. Session 46 assumed `_authenticated/...`
for the admin-shell and dashboard routes without surfacing it; that scheme is
now known to be wrong-road.

**Decision to make:** define the agreed-upon default path shape for the app.
Context: there will be four roles — superadmin → admin → coordinator → auditor.
The admin dashboard is **admin-only** and its paths should be `admin/`-prefixed:
`/admin/dashboard`, `/admin/contracts`, `/admin/contracts/[id]`, etc. Decide the
full shape — how the admin surface and the (future) coordinator / auditor
surfaces are partitioned in the URL space — then migrate the M1.2 routes onto it.

**Affected by the decision:** Session 46 built the Contract admin routes on the
pre-decision `_authenticated/contracts/...` scheme (route files + every `Link` /
`navigate` path in the shell and contract pages). Once the path shape is agreed,
migrating them is mechanical but touches all of those call sites.
