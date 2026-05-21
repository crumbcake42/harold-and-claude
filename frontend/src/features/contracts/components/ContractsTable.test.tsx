import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ContractsTable } from "@/features/contracts/components/ContractsTable";
import { sampleContracts } from "@/features/contracts/fixtures";

describe("ContractsTable", () => {
  it("renders a row per contract", () => {
    render(<ContractsTable contracts={sampleContracts} onEdit={vi.fn()} onDelete={vi.fn()} />);

    expect(screen.getByText("FY24-001")).toBeInTheDocument();
    expect(screen.getByText("FY25-014")).toBeInTheDocument();
    expect(screen.getByText("FY23-099")).toBeInTheDocument();
  });

  it("renders an em dash for a missing end date", () => {
    render(<ContractsTable contracts={sampleContracts} onEdit={vi.fn()} onDelete={vi.fn()} />);

    expect(screen.getByText("—")).toBeInTheDocument();
  });

  it("calls onEdit when the contract label is clicked", async () => {
    const user = userEvent.setup();
    const onEdit = vi.fn();
    render(<ContractsTable contracts={sampleContracts} onEdit={onEdit} onDelete={vi.fn()} />);

    await user.click(screen.getByText("Acme FY24"));

    expect(onEdit).toHaveBeenCalledWith(sampleContracts[0]);
  });

  it("calls onDelete when a row's delete action is clicked", async () => {
    const user = userEvent.setup();
    const onDelete = vi.fn();
    render(<ContractsTable contracts={sampleContracts} onEdit={vi.fn()} onDelete={onDelete} />);

    await user.click(screen.getByRole("button", { name: "Delete Acme FY24" }));

    expect(onDelete).toHaveBeenCalledWith(sampleContracts[0]);
  });
});
