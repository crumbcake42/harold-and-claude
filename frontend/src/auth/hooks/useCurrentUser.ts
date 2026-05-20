// useCurrentUser — the canonical hook for the current-user query (ADR-0063).
//
// Components read this. The _authenticated route guard reads
// currentUserQueryOptions from @/auth/api directly instead, because its
// beforeLoad runs outside React.

import { useQuery } from "@tanstack/react-query";

import { currentUserQueryOptions } from "@/auth/api";

export function useCurrentUser() {
  return useQuery(currentUserQueryOptions());
}
