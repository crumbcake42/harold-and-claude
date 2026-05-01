---
name: no pre-answering decisions in sessions
description: Do not write a position into a planning file before user approval; recommendations in chat are welcomed but do not pre-decide
type: feedback
originSessionId: 924ceee8-3bbe-402c-9218-8cd7036c114d
---
In conceptualization sessions, do not write a position into a planning file before the user explicitly approves it. The artifact is the deliberation. Recommendations in chat are welcome (and expected when canvassing decisions per the STOP-AND-CONFIRM gate); they do not pre-decide. The anti-patterns this rule guards against are *writing the answer into a file before agreement* and *eliminating options before the doc canvasses them*. Both remain prohibited.

**Why:** Two incidents on 2026-04-28 where decisions were stacked or pre-answered in files before the doc was written. The STOP-AND-CONFIRM gate in `planning/handoff.md` is the durable enforcement mechanism. The gate was revised on 2026-04-29 to allow recommendations — the gate is on writes (ADRs, planning files), not on opinions.

**How to apply:** In the proposal turn: surface the fork, present 2–3 candidate positions with tradeoffs, recommend a position with reasoning (per the gate, this is now expected). Stop. Do not write planning files. Wait for explicit approval (or amendments) before touching files. The Plan Mode plan file under `.claude/plans/` is harness scratch, not a planning artifact, and may be written before approval.
