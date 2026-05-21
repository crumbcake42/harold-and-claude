import { PlusIcon, XIcon } from "@phosphor-icons/react";
import type { Control, FieldErrors, UseFormRegister } from "react-hook-form";
import { useFieldArray } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { Field, FieldError } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import type { ContractFormValues } from "@/features/contracts/form";

interface FeeScheduleEditorProps {
  control: Control<ContractFormValues>;
  register: UseFormRegister<ContractFormValues>;
  errors: FieldErrors<ContractFormValues>;
}

// The bespoke editor for a Contract's flat-fee schedule — the JSONB
// `code_flat_fee_schedule` collection (ADR-0043). A repeatable list of
// {code_type, fee} rows over react-hook-form's useFieldArray. Contract-
// specific by design: it does not generalize to the other roster entities.
export function FeeScheduleEditor({ control, register, errors }: FeeScheduleEditorProps) {
  const { fields, append, remove } = useFieldArray({
    control,
    name: "code_flat_fee_schedule",
  });

  return (
    <div className="flex flex-col gap-3">
      <div>
        <span className="text-sm font-medium">Flat-fee schedule</span>
        <p className="text-xs text-muted-foreground">
          Default flat fee per WA code type. A code type with no entry resolves as unpriced.
        </p>
      </div>

      {fields.length === 0 ? (
        <p className="text-xs text-muted-foreground">No fee codes yet.</p>
      ) : (
        <div className="flex flex-col gap-2">
          {fields.map((field, index) => {
            const rowErrors = errors.code_flat_fee_schedule?.[index];
            return (
              <div key={field.id} className="flex items-start gap-2">
                <Field className="flex-1" data-invalid={!!rowErrors?.code_type}>
                  <Input
                    placeholder="Code type"
                    aria-label={`Code type, row ${index + 1}`}
                    aria-invalid={!!rowErrors?.code_type}
                    {...register(`code_flat_fee_schedule.${index}.code_type`)}
                  />
                  <FieldError errors={[rowErrors?.code_type]} />
                </Field>
                <Field className="w-32" data-invalid={!!rowErrors?.fee}>
                  <Input
                    placeholder="Fee"
                    inputMode="decimal"
                    aria-label={`Fee, row ${index + 1}`}
                    aria-invalid={!!rowErrors?.fee}
                    {...register(`code_flat_fee_schedule.${index}.fee`)}
                  />
                  <FieldError errors={[rowErrors?.fee]} />
                </Field>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  aria-label={`Remove fee code, row ${index + 1}`}
                  onClick={() => remove(index)}
                >
                  <XIcon />
                </Button>
              </div>
            );
          })}
        </div>
      )}

      <Button
        type="button"
        variant="outline"
        size="sm"
        className="self-start"
        onClick={() => append({ code_type: "", fee: "" })}
      >
        <PlusIcon />
        Add code
      </Button>
    </div>
  );
}
