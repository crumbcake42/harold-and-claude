// Sample Contract data for tests and stories. Not imported by production
// code — tree-shaken out of the app bundle.

import type { ContractRead } from "@/api/generated/types.gen";

export function makeContract(overrides: Partial<ContractRead> = {}): ContractRead {
  return {
    id: "00000000-0000-0000-0000-000000000001",
    contract_number: "FY24-001",
    name: "Acme FY24",
    start_date: "2024-01-01",
    end_date: "2024-12-31",
    code_flat_fee_schedule: [
      { code_type: "ACP-7", fee: "1200.00" },
      { code_type: "ACP-8", fee: "950.00" },
    ],
    validity: "active",
    display_label: "Acme FY24",
    created_at: "2026-05-20T10:00:00Z",
    created_by: "00000000-0000-0000-0000-0000000000aa",
    updated_at: "2026-05-21T10:00:00Z",
    updated_by: "00000000-0000-0000-0000-0000000000aa",
    ...overrides,
  };
}

export const sampleContracts: ContractRead[] = [
  makeContract(),
  makeContract({
    id: "00000000-0000-0000-0000-000000000002",
    contract_number: "FY25-014",
    name: null,
    start_date: "2025-06-01",
    end_date: null,
    code_flat_fee_schedule: [],
    validity: "pending",
    display_label: "C5-014",
  }),
  makeContract({
    id: "00000000-0000-0000-0000-000000000003",
    contract_number: "FY23-099",
    name: "Initech FY23",
    start_date: "2023-01-01",
    end_date: "2023-12-31",
    validity: "expired",
    display_label: "Initech FY23",
  }),
];
