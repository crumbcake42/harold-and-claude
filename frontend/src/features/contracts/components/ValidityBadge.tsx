import type { ContractRead } from "@/api/generated/types.gen";
import { Badge } from "@/components/ui/badge";

// Renders a Contract's derived validity (ADR-0043: pending / active /
// expired) as a status badge. `validity` is computed by the backend from
// the contract dates — it is never edited.
type Validity = ContractRead["validity"];

const VARIANT: Record<Validity, "default" | "secondary" | "outline"> = {
  active: "default",
  pending: "secondary",
  expired: "outline",
};

export function ValidityBadge({ validity }: { validity: Validity }) {
  return (
    <Badge variant={VARIANT[validity]} className="capitalize">
      {validity}
    </Badge>
  );
}
