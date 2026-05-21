import type { ContractRead } from "@/api/generated/types.gen";
import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";

interface DeleteContractDialogProps {
  /** The contract pending deletion, or null when the dialog is closed. */
  contract: ContractRead | null;
  isPending: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

// Confirmation dialog for deleting a contract. Open state is derived from
// `contract` (non-null = open). The confirm button is a plain destructive
// Button rather than AlertDialogAction so the dialog stays open during the
// request — the page closes it by clearing `contract` on success, and
// leaves it open on error so the user can retry.
export function DeleteContractDialog({
  contract,
  isPending,
  onConfirm,
  onCancel,
}: DeleteContractDialogProps) {
  return (
    <AlertDialog
      open={contract !== null}
      onOpenChange={(open) => {
        if (!open) onCancel();
      }}
    >
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Delete contract?</AlertDialogTitle>
          <AlertDialogDescription>
            {contract
              ? `"${contract.display_label}" will be removed. This action cannot be undone.`
              : ""}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={isPending}>Cancel</AlertDialogCancel>
          <Button variant="destructive" onClick={onConfirm} disabled={isPending}>
            {isPending ? "Deleting…" : "Delete"}
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
