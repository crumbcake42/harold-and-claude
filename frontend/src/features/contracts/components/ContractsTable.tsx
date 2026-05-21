import { PencilIcon, TrashIcon } from "@phosphor-icons/react";

import type { ContractRead } from "@/api/generated/types.gen";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ValidityBadge } from "@/features/contracts/components/ValidityBadge";

interface ContractsTableProps {
  contracts: ContractRead[];
  onEdit: (contract: ContractRead) => void;
  onDelete: (contract: ContractRead) => void;
}

// The contracts overview table — presentational: rows in, edit/delete
// callbacks out. The contract label is a button (the accessible form of
// "click the row to edit"); the actions cell repeats edit + offers delete.
// Empty / loading / error states are the page's concern.
export function ContractsTable({ contracts, onEdit, onDelete }: ContractsTableProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Contract</TableHead>
          <TableHead>Number</TableHead>
          <TableHead>Validity</TableHead>
          <TableHead>Start date</TableHead>
          <TableHead>End date</TableHead>
          <TableHead className="text-right">Fee codes</TableHead>
          <TableHead className="sr-only">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {contracts.map((contract) => (
          <TableRow key={contract.id}>
            <TableCell>
              <button
                type="button"
                onClick={() => onEdit(contract)}
                className="font-medium text-foreground hover:underline"
              >
                {contract.display_label}
              </button>
            </TableCell>
            <TableCell className="text-muted-foreground">{contract.contract_number}</TableCell>
            <TableCell>
              <ValidityBadge validity={contract.validity} />
            </TableCell>
            <TableCell className="text-muted-foreground">{contract.start_date}</TableCell>
            <TableCell className="text-muted-foreground">{contract.end_date ?? "—"}</TableCell>
            <TableCell className="text-right text-muted-foreground tabular-nums">
              {contract.code_flat_fee_schedule.length}
            </TableCell>
            <TableCell>
              <div className="flex justify-end gap-1">
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label={`Edit ${contract.display_label}`}
                  onClick={() => onEdit(contract)}
                >
                  <PencilIcon />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label={`Delete ${contract.display_label}`}
                  onClick={() => onDelete(contract)}
                >
                  <TrashIcon />
                </Button>
              </div>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
