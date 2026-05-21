import { CaretLeftIcon } from "@phosphor-icons/react";
import { Link, useNavigate } from "@tanstack/react-router";
import { toast } from "sonner";

import { Card, CardContent } from "@/components/ui/card";
import { ContractForm } from "@/features/contracts/components/ContractForm";
import { emptyContractForm, formValuesToWriteRequest } from "@/features/contracts/form";
import type { ContractFormValues } from "@/features/contracts/form";
import { useCreateContract } from "@/features/contracts/hooks/useCreateContract";
import { apiErrorMessage } from "@/lib/apiError";

// Create-contract page. Owns the mutation, the success/error toast, and
// post-submit navigation; the form itself is the routing-agnostic
// ContractForm feature component.
export function ContractCreatePage() {
  const navigate = useNavigate();
  const createContract = useCreateContract();

  async function handleSubmit(values: ContractFormValues) {
    try {
      await createContract.mutateAsync({ body: formValuesToWriteRequest(values) });
      toast.success("Contract created");
      await navigate({ to: "/admin/contracts" });
    } catch (error) {
      toast.error(apiErrorMessage(error, "Could not create the contract."));
    }
  }

  return (
    <div className="max-w-2xl">
      <Link
        to="/admin/contracts"
        className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
      >
        <CaretLeftIcon />
        Contracts
      </Link>
      <h1 className="mt-2 text-lg font-semibold">New contract</h1>
      <Card className="mt-4">
        <CardContent>
          <ContractForm
            defaultValues={emptyContractForm()}
            onSubmit={handleSubmit}
            onCancel={() => navigate({ to: "/admin/contracts" })}
            isPending={createContract.isPending}
            submitLabel="Create contract"
          />
        </CardContent>
      </Card>
    </div>
  );
}
