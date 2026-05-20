import type { Meta, StoryObj } from "@storybook/react-vite";

import { LoginForm } from "@/auth/components/LoginForm";

const meta = {
  title: "auth/LoginForm",
  component: LoginForm,
  args: {
    onSubmit: () => {},
    isPending: false,
  },
} satisfies Meta<typeof LoginForm>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Pending: Story = {
  args: { isPending: true },
};
