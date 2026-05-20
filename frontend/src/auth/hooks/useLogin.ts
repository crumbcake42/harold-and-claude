import { useMutation, useQueryClient } from "@tanstack/react-query";

import { currentUserQueryKey, loginMutation } from "@/auth/api";

// useLogin — wraps the login mutation. On success it primes the current-user
// cache with the Caller the login response already returned via setQueryData,
// NOT invalidateQueries: the /login page has no active subscriber to the
// current-user query, so invalidate would mark it stale without refetching,
// and the route guard would then read a stale null and bounce back to /login.
// See ADR-0063. Navigation is the caller's concern, not this hook's.
export function useLogin() {
  const queryClient = useQueryClient();

  return useMutation({
    ...loginMutation(),
    onSuccess: (caller) => {
      queryClient.setQueryData(currentUserQueryKey, caller);
    },
  });
}
