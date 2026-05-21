import { createFileRoute, redirect } from "@tanstack/react-router";

// Root of the authenticated app. Redirects to the caller's highest accessible
// dashboard; only the `/admin` surface exists today, so this is a fixed
// redirect for now. ADR-0077 records the role-dispatch design for when the
// tracker/review surfaces land.
export const Route = createFileRoute("/_authenticated/")({
  beforeLoad: () => {
    throw redirect({ to: "/admin/dashboard" });
  },
});
