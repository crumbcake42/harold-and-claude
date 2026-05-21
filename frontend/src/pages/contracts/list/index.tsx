import { PlusIcon } from "@phosphor-icons/react";
import { useQuery } from "@tanstack/react-query";
import { Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { toast } from "sonner";

import type { ContractRead } from "@/api/generated/types.gen";
import { Button } from "@/components/ui/button";
import { listContractsOptions } from "@/features/contracts/api";
import { ContractsTable } from "@/features/contracts/components/ContractsTable";
import { DeleteContractDialog } from "@/features/contracts/components/DeleteContractDialog";
import { useDeleteContract } from "@/features/contracts/hooks/useDeleteContract";
import { apiErrorMessage } from "@/lib/apiError";

// The contracts overview page. The route loader prefetches the list, so on
// the happy path the table renders without a loading flash; this page still
// owns the loading / error / empty states for cold navigations and refetches.
export function ContractsListPage() {
  const navigate = useNavigate();
  const { data: contracts, isPending, isError, refetch } = useQuery(listContractsOptions());
  const deleteContract = useDeleteContract();
  const [pendingDelete, setPendingDelete] = useState<ContractRead | null>(null);

  async function handleConfirmDelete() {
    if (!pendingDelete) return;
    try {
      await deleteContract.mutateAsync({ path: { contract_id: pendingDelete.id } });
      toast.success("Contract deleted");
      setPendingDelete(null);
    } catch (error) {
      toast.error(apiErrorMessage(error, "Could not delete the contract."));
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold">Contracts</h1>
        <Button asChild>
          <Link to="/admin/contracts/new">
            <PlusIcon />
            New contract
          </Link>
        </Button>
      </div>

      {isPending ? (
        <p className="text-sm text-muted-foreground">Loading contracts…</p>
      ) : isError ? (
        <div className="rounded-md border border-border p-8 text-center">
          <p className="text-sm text-destructive">Could not load contracts.</p>
          <Button variant="outline" size="sm" className="mt-3" onClick={() => refetch()}>
            Retry
          </Button>
        </div>
      ) : contracts.length === 0 ? (
        <div className="rounded-md border border-border p-8 text-center">
          <p className="text-sm text-muted-foreground">No contracts yet.</p>
          <Button asChild variant="outline" size="sm" className="mt-3">
            <Link to="/admin/contracts/new">
              <PlusIcon />
              New contract
            </Link>
          </Button>
        </div>
      ) : (
        <ContractsTable
          contracts={contracts}
          onEdit={(contract) =>
            navigate({
              to: "/admin/contracts/$contractId",
              params: { contractId: contract.id },
            })
          }
          onDelete={setPendingDelete}
        />
      )}

      <DeleteContractDialog
        contract={pendingDelete}
        isPending={deleteContract.isPending}
        onConfirm={handleConfirmDelete}
        onCancel={() => setPendingDelete(null)}
      />
    </div>
  );
}
