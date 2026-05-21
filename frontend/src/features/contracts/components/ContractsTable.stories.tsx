import type { Meta, StoryObj } from "@storybook/react-vite";

import { ContractsTable } from "@/features/contracts/components/ContractsTable";
import { sampleContracts } from "@/features/contracts/fixtures";

const meta = {
  title: "contracts/ContractsTable",
  component: ContractsTable,
  args: {
    onEdit: () => {},
    onDelete: () => {},
  },
} satisfies Meta<typeof ContractsTable>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = { args: { contracts: sampleContracts } };

export const SingleContract: Story = {
  args: { contracts: sampleContracts.slice(0, 1) },
};
