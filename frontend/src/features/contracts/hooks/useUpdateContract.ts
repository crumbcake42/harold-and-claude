import { useMutation, useQueryClient } from "@tanstack/react-query";

import {
  contractQueryKey,
  contractsQueryKey,
  updateContractMutation,
} from "@/features/contracts/api";

// useUpdateContract — wraps the update mutation. On success it invalidates
// both the contracts list and the edited contract's detail query, so a
// later visit to either reflects the change. Toast + navigation live in
// the page.
export function useUpdateContract() {
  const queryClient = useQueryClient();

  return useMutation({
    ...updateContractMutation(),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: contractsQueryKey() });
      queryClient.invalidateQueries({
        queryKey: contractQueryKey({ path: variables.path }),
      });
    },
  });
}
