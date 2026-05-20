// Current-user query definition.
//
// Hand-written rather than a generated re-export: the queryFn catches the 401
// (the logged-out steady state) and returns null instead of throwing, so the
// route guard and useCurrentUser both get a clean null on no-session.
//
// Lives in api/ rather than hooks/ because currentUserQueryOptions is consumed
// outside React by the _authenticated route guard's beforeLoad. src/auth/ is
// exempt from the api-barrel rule and may import @/api/generated directly.

import { meAuthMeGet } from "@/api/generated";

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
    // Keep the result fresh for a minute; auth state doesn't churn that fast
    // and we want navigation transitions to be snappy.
    staleTime: 60_000,
  };
}
