import { standardSchemaResolver } from "@hookform/resolvers/standard-schema";
import type { ReactNode } from "react";
import { useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { Field, FieldDescription, FieldError, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { FeeScheduleEditor } from "@/features/contracts/components/FeeScheduleEditor";
import { contractFormSchema } from "@/features/contracts/form";
import type { ContractFormValues } from "@/features/contracts/form";

interface ContractFormProps {
  defaultValues: ContractFormValues;
  onSubmit: (values: ContractFormValues) => void | Promise<void>;
  onCancel: () => void;
  isPending: boolean;
  submitLabel: string;
  /** Optional read-only panel (validity + audit metadata) shown on edit. */
  metadata?: ReactNode;
}

// The create + edit form for a Contract — props in, callbacks out. The
// mutation, toast, and navigation live in the page; this component owns
// only client-side validation (Zod) and field composition. Server errors
// are surfaced by the page as a toast (Step 2.2c decision).
export function ContractForm({
  defaultValues,
  onSubmit,
  onCancel,
  isPending,
  submitLabel,
  metadata,
}: ContractFormProps) {
  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
  } = useForm<ContractFormValues>({
    resolver: standardSchemaResolver(contractFormSchema),
    defaultValues,
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate className="flex flex-col gap-6">
      <FieldGroup>
        <Field data-invalid={!!errors.contract_number}>
          <FieldLabel htmlFor="contract_number">
            Contract number <span className="text-destructive">*</span>
          </FieldLabel>
          <Input
            id="contract_number"
            aria-invalid={!!errors.contract_number}
            {...register("contract_number")}
          />
          <FieldError errors={[errors.contract_number]} />
        </Field>

        <Field>
          <FieldLabel htmlFor="name">Name</FieldLabel>
          <Input id="name" {...register("name")} />
          <FieldDescription>
            Optional. A label is derived from the contract number when left blank.
          </FieldDescription>
        </Field>

        <Field data-invalid={!!errors.start_date}>
          <FieldLabel htmlFor="start_date">
            Start date <span className="text-destructive">*</span>
          </FieldLabel>
          <Input
            id="start_date"
            type="date"
            aria-invalid={!!errors.start_date}
            {...register("start_date")}
          />
          <FieldError errors={[errors.start_date]} />
        </Field>

        <Field data-invalid={!!errors.end_date}>
          <FieldLabel htmlFor="end_date">End date</FieldLabel>
          <Input
            id="end_date"
            type="date"
            aria-invalid={!!errors.end_date}
            {...register("end_date")}
          />
          <FieldError errors={[errors.end_date]} />
        </Field>
      </FieldGroup>

      <FeeScheduleEditor control={control} register={register} errors={errors} />

      {metadata}

      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={onCancel} disabled={isPending}>
          Cancel
        </Button>
        <Button type="submit" disabled={isPending}>
          {isPending ? "Saving…" : submitLabel}
        </Button>
      </div>
    </form>
  );
}
