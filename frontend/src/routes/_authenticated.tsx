import { createFileRoute, redirect } from "@tanstack/react-router";

import { currentUserQueryOptions } from "@/auth/api";

// Pathless route -- the authentication guard for the whole app. It contributes
// no URL segment and renders no chrome: a component-less route defaults to an
// <Outlet/>, and per-surface chrome lives on each surface layout route (the
// `admin` layout renders AdminShellLayout). See ADR-0077.
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
});
