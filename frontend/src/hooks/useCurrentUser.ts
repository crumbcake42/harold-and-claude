// useCurrentUser — TanStack Query hook wrapping GET /auth/me.
//
// Returns the Caller payload when authenticated; returns undefined (and
// surfaces .error) on 401. Consumers (the _authenticated route layout,
// the logged-in shell header, etc.) read this hook to decide UI state.
//
// retry: false because 401 is an expected steady-state for logged-out
// users; retrying on it just delays the redirect.

import { useQuery } from "@tanstack/react-query";

import { meAuthMeGet } from "../api/generated";

export const currentUserQueryKey = ["auth", "me"] as const;

export function currentUserQueryOptions() {
  return {
    queryKey: currentUserQueryKey,
    queryFn: async () => {
      const response = await meAuthMeGet({ throwOnError: false });
      if (response.error) {
        // 401 is the "not logged in" signal; treat any error as no-user.
        return null;
      }
      return response.data ?? null;
    },
    retry: false,
    // Keep the result fresh for a minute; auth state doesn't churn that
    // fast and we want navigation transitions to be snappy.
    staleTime: 60_000,
  };
}

export function useCurrentUser() {
  return useQuery(currentUserQueryOptions());
}
