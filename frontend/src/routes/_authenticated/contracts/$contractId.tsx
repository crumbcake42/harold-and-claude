import { createFileRoute } from "@tanstack/react-router";

import { ContractEditError, ContractEditPage } from "@/pages/contracts/edit";
import { loadContract } from "@/pages/contracts/edit/loader";

export const Route = createFileRoute("/_authenticated/contracts/$contractId")({
  loader: ({ context, params }) => loadContract(context.queryClient, params.contractId),
  component: ContractEditPage,
  errorComponent: ContractEditError,
});
