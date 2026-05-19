import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createFileRoute, useNavigate } from "@tanstack/react-router";

import { logoutAuthLogoutPost } from "../../api";
import { useCurrentUser, currentUserQueryKey } from "../../hooks/useCurrentUser";

export const Route = createFileRoute("/_authenticated/")({
  component: AdminShell,
});

function AdminShell() {
  const { data: user } = useCurrentUser();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const logoutMutation = useMutation({
    mutationFn: () => logoutAuthLogoutPost(),
    onSettled: async () => {
      await queryClient.invalidateQueries({ queryKey: currentUserQueryKey });
      navigate({ to: "/login" });
    },
  });

  return (
    <main style={{ fontFamily: "system-ui", padding: "2rem" }}>
      <header
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "baseline",
          borderBottom: "1px solid #ddd",
          paddingBottom: "1rem",
        }}
      >
        <h1 style={{ margin: 0 }}>sca-tracker — admin</h1>
        <div>
          <span style={{ marginRight: "1rem", color: "#555" }}>{user?.username ?? "—"}</span>
          <button
            type="button"
            onClick={() => logoutMutation.mutate()}
            disabled={logoutMutation.isPending}
          >
            {logoutMutation.isPending ? "signing out…" : "sign out"}
          </button>
        </div>
      </header>
      <section style={{ marginTop: "1.5rem", color: "#666" }}>
        <p>M1.1 auth shell online. Per-entity admin pages land in M1.2.</p>
      </section>
    </main>
  );
}
