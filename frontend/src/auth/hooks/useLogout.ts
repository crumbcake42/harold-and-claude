import { useMutation, useQueryClient } from "@tanstack/react-query";

import { currentUserQueryKey, logoutMutation } from "@/auth/api";

// useLogout — wraps the logout mutation. onSettled (not onSuccess) invalidates
// the current-user query: the admin shell subscribes to useCurrentUser, so the
// invalidation refetches, sees the now-revoked session as null, and writes
// that into the cache. Running on settle means a logout that races an
// already-expired session still clears the cache. Navigation is the caller's
// concern, not this hook's. See ADR-0063.
export function useLogout() {
  const queryClient = useQueryClient();

  return useMutation({
    ...logoutMutation(),
    onSettled: () => queryClient.invalidateQueries({ queryKey: currentUserQueryKey }),
  });
}
