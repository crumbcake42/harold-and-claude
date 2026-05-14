# Post-MVP Feature Candidates

## File contract

**Holds:** Post-MVP feature candidates — name, one-line description, one-line "why interesting." Holding pen between now and Step 7's `mvp.md` out-of-scope section.
**Update when:** A feature idea surfaces that's worth remembering but explicitly out of MVP scope. Consolidated into `mvp.md`'s out-of-scope section when Step 7 runs.

---

## Per-page Daily Log assignment

- **What:** Associate individual pages of a Daily Log document with specific Time Entries (and possibly Sample Batches).
- **Why interesting:** Enables a side-by-side review UI where Time Entries are displayed alongside their source-document pages, giving a visual audit of recorded entities against narrative evidence.

## Track-this pin for blockers (notification-coupled)

- **What:** A "track this" engagement trigger on derived blockers (ADR-0032) that materializes the blocker Note without writing commentary or dismissing. Bundled with a notification system that pings the pinning coordinator on state changes.
- **Why interesting:** Without notifications, pinning is functionally equivalent to "the panel already shows this" — value collapses. With notifications, it becomes a real "watch this" affordance for blockers the coordinator is actively monitoring (e.g., waiting on a vendor response). Pairs naturally with the notification batch below.

## Structured blocker assignment + notifications

- **What:** Add `assigned_to: nullable User` field to blocker Notes (ADR-0032), with `(re)assign_blocker` commands, a my-blockers queryable view, and a reassignment audit chain (partial supersession of ADR-0018's no-history stance for blocker Notes). Coupled with push/in-app notifications so assignees know they were assigned.
- **Why interesting:** Note conventions ("Sarah, please push this") cover ~70–80% of operational value for MVP, but lose queryability, surface-in-user's-UI, and time-on-plate accounting. Structural assignment becomes a clear win once notifications exist, because assignment then actually pings the assignee. Bundles with the pin above and with the cross-project Sample Batch reassignment below — all three benefit from the same notification substrate.

## Structured cross-project Sample Batch reassignment

- **What:** A `reassign_sample_batch_project(batch, new_project, new_wa_code)` command that moves a misfiled batch from Project X to Project Y in one atomic act, with notification to Project Y's coordinator that the batch is incoming.
- **Why interesting:** The misfiled-COC scenario is operationally common (per session 6 deliberation). MVP handles it via `dismiss #9` (chain-dismisses to non-billable) + `relink_sample_batch_wa_code` to a code on Project Y — two acts, no notification, but auditable. The structured command compresses to one act and adds the cross-project handoff signal Project Y's coordinator needs. Pairs with notification batch above.

## SCA-side RFP rejection notification

- **What:** Automated trigger for `reopen_project(project, rfp_reason='rfp_rejected')` when SCA's portal signals an RFP rejection. Requires SCA portal integration (event ingest) and notification to the coordinator that the project has been reopened.
- **Why interesting:** ADR-0037 leaves `reopen_project` as a manual coordinator action. With portal integration, rejection becomes a system-detected event; the project reopens automatically with the audit chain intact, and the coordinator is pinged. Reduces the latency between SCA-side rejection and coordinator awareness, which today depends on the coordinator noticing an email or checking the portal. Pairs with the notification batch above.

## Stale-RFP signal (long-tail SCA non-response)

- **What:** A derived signal on a project with an RFP in `saved` state for an extended period without SCA-side acknowledgement (approval payment, rejection, etc.). Surfaces in the coordinator UI as a "watch this" affordance; not a closure blocker (the project is already closed).
- **Why interesting:** ADR-0037 leaves `saved` RFPs sitting indefinitely. In practice, SCA-side payment flows are bounded but can stall. A stale-RFP signal gives the coordinator a queryable view of "submissions waiting on SCA" without forcing additional state into the entity. Implementation can be a derived predicate over `(rfp.state = 'saved' AND rfp.saved_at < now() - threshold)`; the threshold is operational policy, not a domain decision.

*(The former "Project → Contract reassignment" candidate — `reassign_project_contract` — was **dissolved by ADR-0044** and removed: with the Contract re-attached to the WABundle and made mutable in MVP via `edit_wabundle` / `issue_wa`, and all money-bearing values derived at read time, there is no heavy cascade to defer.)*
