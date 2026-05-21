import { createFileRoute, redirect } from "@tanstack/react-router";

// `/admin` carries no page of its own -- the surface root redirects to the
// dashboard (same role `_authenticated/index.tsx` plays for `/`). Without this
// index route, `/admin` would render the shell chrome with an empty <Outlet/>.
// See ADR-0077.
export const Route = createFileRoute("/_authenticated/admin/")({
  beforeLoad: () => {
    throw redirect({ to: "/admin/dashboard" });
  },
});
