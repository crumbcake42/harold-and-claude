import type { Meta, StoryObj } from "@storybook/react-vite";
import { useForm } from "react-hook-form";

import { FeeScheduleEditor } from "@/features/contracts/components/FeeScheduleEditor";
import type { ContractFormValues } from "@/features/contracts/form";
import { emptyContractForm } from "@/features/contracts/form";

// FeeScheduleEditor takes react-hook-form's control/register/errors, so the
// story wraps it in a host form to supply them.
function FeeScheduleEditorHarness({
  initial,
}: {
  initial: ContractFormValues["code_flat_fee_schedule"];
}) {
  const {
    control,
    register,
    formState: { errors },
  } = useForm<ContractFormValues>({
    defaultValues: { ...emptyContractForm(), code_flat_fee_schedule: initial },
  });
  return <FeeScheduleEditor control={control} register={register} errors={errors} />;
}

const meta: Meta<typeof FeeScheduleEditor> = {
  title: "contracts/FeeScheduleEditor",
  component: FeeScheduleEditor,
};

export default meta;

type Story = StoryObj<typeof FeeScheduleEditor>;

export const Empty: Story = {
  render: () => <FeeScheduleEditorHarness initial={[]} />,
};

export const WithEntries: Story = {
  render: () => (
    <FeeScheduleEditorHarness
      initial={[
        { code_type: "ACP-7", fee: "1200.00" },
        { code_type: "ACP-8", fee: "950.00" },
      ]}
    />
  ),
};
