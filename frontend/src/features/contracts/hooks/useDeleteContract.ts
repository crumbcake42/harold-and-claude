import { useMutation, useQueryClient } from "@tanstack/react-query";

import { contractsQueryKey, deleteContractMutation } from "@/features/contracts/api";

// useDeleteContract — wraps the delete mutation and invalidates the
// contracts list on success so the removed row disappears. The confirm
// dialog, toast, and navigation are the page's concern.
export function useDeleteContract() {
  const queryClient = useQueryClient();

  return useMutation({
    ...deleteContractMutation(),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: contractsQueryKey() }),
  });
}
