import { useMutation, useQueryClient } from "@tanstack/react-query";

import { contractsQueryKey, createContractMutation } from "@/features/contracts/api";

// useCreateContract — wraps the create mutation and invalidates the
// contracts list on success so the new row appears. The success toast and
// navigation are the page's concern, not this hook's.
export function useCreateContract() {
  const queryClient = useQueryClient();

  return useMutation({
    ...createContractMutation(),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: contractsQueryKey() }),
  });
}
