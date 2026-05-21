// Contracts API barrel — the single import surface for Contract data
// access. Thin re-exports of the generated TanStack Query helpers under
// domain-operation names; feature components, hooks, and pages import from
// here, never from @/api/generated/ directly (ADR-0064 / ADR-0066).

export {
  listContractsContractsGetOptions as listContractsOptions,
  listContractsContractsGetQueryKey as contractsQueryKey,
  getContractContractsContractIdGetOptions as contractOptions,
  getContractContractsContractIdGetQueryKey as contractQueryKey,
  createContractContractsPostMutation as createContractMutation,
  updateContractContractsContractIdPutMutation as updateContractMutation,
  deleteContractContractsContractIdDeleteMutation as deleteContractMutation,
} from "@/api/generated/@tanstack/react-query.gen";
