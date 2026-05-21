import { CaretLeftIcon } from "@phosphor-icons/react";
import { useSuspenseQuery } from "@tanstack/react-query";
import { Link, getRouteApi, useNavigate } from "@tanstack/react-router";
import { toast } from "sonner";

import type { ContractRead } from "@/api/generated/types.gen";
import { Card, CardContent } from "@/components/ui/card";
import { contractOptions } from "@/features/contracts/api";
import { ContractForm } from "@/features/contracts/components/ContractForm";
import { ValidityBadge } from "@/features/contracts/components/ValidityBadge";
import { contractToFormValues, formValuesToWriteRequest } from "@/features/contracts/form";
import type { ContractFormValues } from "@/features/contracts/form";
import { useUpdateContract } from "@/features/contracts/hooks/useUpdateContract";
import { apiErrorMessage } from "@/lib/apiError";

const routeApi = getRouteApi("/_authenticated/contracts/$contractId");

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString();
}

// Read-only panel shown below the edit form: the derived validity and the
// audit timestamps. created_by / updated_by are UUIDs with no name lookup
// yet, so they are omitted until a user-name resolution exists.
function ContractMetadata({ contract }: { contract: ContractRead }) {
  return (
    <div className="flex flex-wrap items-center gap-x-4 gap-y-1 border-t border-border pt-4 text-xs text-muted-foreground">
      <span className="flex items-center gap-1.5">
        Validity
        <ValidityBadge validity={contract.validity} />
      </span>
      <span>Created {formatDate(contract.created_at)}</span>
      <span>Updated {formatDate(contract.updated_at)}</span>
    </div>
  );
}

// Edit-contract page. The route loader has already resolved the contract
// into the query cache, so useSuspenseQuery reads it without a flash; this
// page owns the mutation, toasts, and post-submit navigation.
export function ContractEditPage() {
  const { contractId } = routeApi.useParams();
  const navigate = useNavigate();
  const { data: contract } = useSuspenseQuery(
    contractOptions({ path: { contract_id: contractId } }),
  );
  const updateContract = useUpdateContract();

  async function handleSubmit(values: ContractFormValues) {
    try {
      await updateContract.mutateAsync({
        path: { contract_id: contractId },
        body: formValuesToWriteRequest(values),
      });
      toast.success("Contract updated");
      await navigate({ to: "/contracts" });
    } catch (error) {
      toast.error(apiErrorMessage(error, "Could not update the contract."));
    }
  }

  return (
    <div className="max-w-2xl">
      <Link
        to="/contracts"
        className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
      >
        <CaretLeftIcon />
        Contracts
      </Link>
      <h1 className="mt-2 text-lg font-semibold">{contract.display_label}</h1>
      <Card className="mt-4">
        <CardContent>
          <ContractForm
            defaultValues={contractToFormValues(contract)}
            onSubmit={handleSubmit}
            onCancel={() => navigate({ to: "/contracts" })}
            isPending={updateContract.isPending}
            submitLabel="Save changes"
            metadata={<ContractMetadata contract={contract} />}
          />
        </CardContent>
      </Card>
    </div>
  );
}

// Route errorComponent — rendered when the loader rejects (typically a 404
// for an unknown contract id).
export function ContractEditError() {
  return (
    <div className="max-w-2xl">
      <Link
        to="/contracts"
        className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
      >
        <CaretLeftIcon />
        Contracts
      </Link>
      <div className="mt-4 rounded-md border border-border p-8 text-center">
        <p className="text-sm text-muted-foreground">This contract could not be found.</p>
      </div>
    </div>
  );
}
