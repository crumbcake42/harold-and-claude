import type { Meta, StoryObj } from "@storybook/react-vite";

import { ValidityBadge } from "@/features/contracts/components/ValidityBadge";

const meta = {
  title: "contracts/ValidityBadge",
  component: ValidityBadge,
} satisfies Meta<typeof ValidityBadge>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Active: Story = { args: { validity: "active" } };
export const Pending: Story = { args: { validity: "pending" } };
export const Expired: Story = { args: { validity: "expired" } };
