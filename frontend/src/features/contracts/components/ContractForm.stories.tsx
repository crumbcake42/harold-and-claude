import type { Meta, StoryObj } from "@storybook/react-vite";

import { ContractForm } from "@/features/contracts/components/ContractForm";
import { makeContract } from "@/features/contracts/fixtures";
import { contractToFormValues, emptyContractForm } from "@/features/contracts/form";

const meta = {
  title: "contracts/ContractForm",
  component: ContractForm,
  args: {
    onSubmit: () => {},
    onCancel: () => {},
    isPending: false,
  },
} satisfies Meta<typeof ContractForm>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Create: Story = {
  args: {
    defaultValues: emptyContractForm(),
    submitLabel: "Create contract",
  },
};

export const Edit: Story = {
  args: {
    defaultValues: contractToFormValues(makeContract()),
    submitLabel: "Save changes",
  },
};
