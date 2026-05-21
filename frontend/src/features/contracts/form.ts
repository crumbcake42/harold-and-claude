// Contract form schema + the mapping between form values and the API
// wire types. Kept as a concretely-named module rather than a `services/`
// folder (ADR-0066). The form holds every field as a string (what inputs
// produce); the mappers convert to / from `ContractWriteRequest` and
// `ContractRead`, where optional fields are `null` and absent ones omitted.

import { z } from "zod";

import type { ContractRead, ContractWriteRequest } from "@/api/generated/types.gen";

// A fee is a positive money amount — integer or up to two decimal places.
// Stored and sent as a string; the backend re-coerces it to Decimal.
const feeEntrySchema = z.object({
  code_type: z.string().trim().min(1, "Code type is required"),
  fee: z
    .string()
    .min(1, "Fee is required")
    .regex(/^\d+(\.\d{1,2})?$/, "Enter a valid amount (e.g. 1200 or 1200.50)"),
});

export const contractFormSchema = z
  .object({
    contract_number: z.string().trim().min(1, "Contract number is required"),
    name: z.string(),
    start_date: z.string().min(1, "Start date is required"),
    end_date: z.string(),
    code_flat_fee_schedule: z.array(feeEntrySchema),
  })
  .refine((v) => !v.end_date || v.end_date >= v.start_date, {
    path: ["end_date"],
    message: "End date must be on or after the start date",
  });

export type ContractFormValues = z.infer<typeof contractFormSchema>;

/** A blank form — the create page's default values. */
export function emptyContractForm(): ContractFormValues {
  return {
    contract_number: "",
    name: "",
    start_date: "",
    end_date: "",
    code_flat_fee_schedule: [],
  };
}

/** Projects a fetched Contract onto editable form values. */
export function contractToFormValues(contract: ContractRead): ContractFormValues {
  return {
    contract_number: contract.contract_number,
    name: contract.name ?? "",
    start_date: contract.start_date,
    end_date: contract.end_date ?? "",
    code_flat_fee_schedule: contract.code_flat_fee_schedule.map((entry) => ({
      code_type: entry.code_type,
      fee: entry.fee,
    })),
  };
}

/** Converts validated form values to the create / update request body. */
export function formValuesToWriteRequest(values: ContractFormValues): ContractWriteRequest {
  return {
    contract_number: values.contract_number.trim(),
    name: values.name.trim() || null,
    start_date: values.start_date,
    end_date: values.end_date || null,
    code_flat_fee_schedule: values.code_flat_fee_schedule.map((entry) => ({
      code_type: entry.code_type.trim(),
      fee: entry.fee,
    })),
  };
}
