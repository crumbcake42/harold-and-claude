import { createFileRoute } from "@tanstack/react-router";

import { AdminShellLayout } from "@/pages/admin-shell";

// The `/admin/*` surface layout route -- owned by the `admin` role (ADR-0077).
// Renders the admin shell chrome; each admin page renders into its <Outlet/>.
// The surface's min-role `beforeLoad` gate is deferred until a second surface
// (tracker/review) exists -- see ADR-0077 and handoff.md Open questions.
export const Route = createFileRoute("/_authenticated/admin")({
  component: AdminShellLayout,
});
