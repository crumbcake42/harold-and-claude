import type { Meta, StoryObj } from "@storybook/react-vite";

import { DeleteContractDialog } from "@/features/contracts/components/DeleteContractDialog";
import { makeContract } from "@/features/contracts/fixtures";

const meta = {
  title: "contracts/DeleteContractDialog",
  component: DeleteContractDialog,
  args: {
    onConfirm: () => {},
    onCancel: () => {},
    isPending: false,
  },
} satisfies Meta<typeof DeleteContractDialog>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Open: Story = { args: { contract: makeContract() } };

export const Deleting: Story = {
  args: { contract: makeContract(), isPending: true },
};
