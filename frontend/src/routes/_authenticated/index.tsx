import { createFileRoute } from "@tanstack/react-router";

import { AdminShellPage } from "@/pages/admin-shell";

export const Route = createFileRoute("/_authenticated/")({
  component: AdminShellPage,
});
