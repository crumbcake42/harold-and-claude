import type { QueryClient } from "@tanstack/react-query";

import { contractOptions } from "@/features/contracts/api";

// Route loader for the edit page. ensureQueryData (not prefetchQuery) so a
// missing / unreachable contract rejects the loader — the route's
// errorComponent then renders "contract not found" instead of the form.
export function loadContract(queryClient: QueryClient, contractId: string) {
  return queryClient.ensureQueryData(contractOptions({ path: { contract_id: contractId } }));
}
