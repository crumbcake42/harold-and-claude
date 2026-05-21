import type { QueryClient } from "@tanstack/react-query";

import { listContractsOptions } from "@/features/contracts/api";

// Route loader for the contracts list. prefetchQuery (not ensureQueryData)
// warms the cache without throwing on failure — a failed load surfaces as
// the page's own inline error + retry, not a route-level error screen.
export function loadContracts(queryClient: QueryClient): Promise<void> {
  return queryClient.prefetchQuery(listContractsOptions());
}
