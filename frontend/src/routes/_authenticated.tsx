import { Outlet, createFileRoute, redirect } from "@tanstack/react-router";

import { currentUserQueryOptions } from "../hooks/useCurrentUser";

export const Route = createFileRoute("/_authenticated")({
  beforeLoad: async ({ context }) => {
    // ensureQueryData reads the cache when fresh, fetches when stale --
    // matches useCurrentUser's hook so we don't double-fire /auth/me.
    const user = await context.queryClient.ensureQueryData(currentUserQueryOptions());
    if (!user) {
      throw redirect({ to: "/login" });
    }
    return { user };
  },
  component: AuthenticatedLayout,
});

function AuthenticatedLayout() {
  return <Outlet />;
}
