---
name: Casual back-and-forth for sca-tracker entity deliberation
description: For entity-discovery work, prefer conversational use-case-driven exchange over enumerated fork-and-table format; agent self-monitors context and flags wrap points
type: feedback
originSessionId: d1424e1e-57ac-4061-ac8b-5d7c0347e817
---
For sca-tracker entity-level deliberation (Step 6a entity roster; Step 6b/6c walks), default to a casual back-and-forth: user describes a use case, agent identifies entities and surfaces tensions inline, user confirms/adjusts/counter-examples. Maintain a running "agreements so far" tally in chat at natural checkpoints (every few exchanges, or whenever a roster item locks in) so wrap-up has clean material to fold in. Recommendations and pushback still expected per CLAUDE.md base rule; STOP-AND-CONFIRM gate still applies to writes.

Also: agent self-monitors its context-window usage and proactively flags wrap-or-compact points. Heuristic thresholds: heads-up around ~70% consumed ("we have headroom for ~N more entities before wrap"); landing call around ~85% ("let's note agreements and plan a continuation session"). Honest caveat: agent cannot read a token counter directly — estimates are based on files loaded plus conversation length.

**Why:** User found the full forks-and-tables format too heavyweight for entity discovery, where ambiguity surfaces best through concrete examples rather than upfront option matrices. Context monitoring is a session-management ask: the user does not want to discover mid-deliberation that we've run out of room without a wrap-up plan.

**How to apply:** During Step 6a/6b/6c (and analogous future entity-discovery work), default to use-case-driven discussion. Reserve enumerated tables for genuinely multi-axis decisions or when the user explicitly asks. Periodically restate the running agreements roster. Flag context-window state proactively at the two thresholds above.
