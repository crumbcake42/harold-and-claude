import { createFileRoute } from "@tanstack/react-router";

import { ContractCreatePage } from "@/pages/contracts/create";

export const Route = createFileRoute("/_authenticated/contracts/new")({
  component: ContractCreatePage,
});
