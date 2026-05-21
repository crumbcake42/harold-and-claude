import { createFileRoute } from "@tanstack/react-router";

import { ContractsListPage } from "@/pages/contracts/list";
import { loadContracts } from "@/pages/contracts/list/loader";

export const Route = createFileRoute("/_authenticated/admin/contracts/")({
  loader: ({ context }) => loadContracts(context.queryClient),
  component: ContractsListPage,
});
