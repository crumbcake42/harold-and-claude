import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ContractForm } from "@/features/contracts/components/ContractForm";
import { emptyContractForm } from "@/features/contracts/form";

function renderForm(props: Partial<Parameters<typeof ContractForm>[0]> = {}) {
  return render(
    <ContractForm
      defaultValues={emptyContractForm()}
      onSubmit={vi.fn()}
      onCancel={vi.fn()}
      isPending={false}
      submitLabel="Create contract"
      {...props}
    />,
  );
}

describe("ContractForm", () => {
  it("renders the contract fields", () => {
    renderForm();

    expect(screen.getByLabelText(/Contract number/)).toBeInTheDocument();
    expect(screen.getByLabelText("Name")).toBeInTheDocument();
    expect(screen.getByLabelText(/Start date/)).toBeInTheDocument();
    expect(screen.getByLabelText("End date")).toBeInTheDocument();
  });

  it("shows validation errors and does not submit when required fields are blank", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    renderForm({ onSubmit });

    await user.click(screen.getByRole("button", { name: "Create contract" }));

    expect(await screen.findByText("Contract number is required")).toBeInTheDocument();
    expect(screen.getByText("Start date is required")).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("submits the entered values", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    renderForm({ onSubmit });

    await user.type(screen.getByLabelText(/Contract number/), "FY24-001");
    await user.type(screen.getByLabelText(/Start date/), "2024-01-01");
    await user.click(screen.getByRole("button", { name: "Create contract" }));

    await waitFor(() => expect(onSubmit).toHaveBeenCalled());
    expect(onSubmit.mock.calls[0][0]).toMatchObject({
      contract_number: "FY24-001",
      start_date: "2024-01-01",
    });
  });

  it("adds a fee-schedule row", async () => {
    const user = userEvent.setup();
    renderForm();

    expect(screen.getByText("No fee codes yet.")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Add code" }));

    expect(screen.getByLabelText("Code type, row 1")).toBeInTheDocument();
    expect(screen.getByLabelText("Fee, row 1")).toBeInTheDocument();
  });

  it("disables the actions while pending", () => {
    renderForm({ isPending: true });

    expect(screen.getByRole("button", { name: "Saving…" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Cancel" })).toBeDisabled();
  });
});
