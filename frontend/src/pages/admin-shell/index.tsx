import { SignOutIcon } from "@phosphor-icons/react";
import { useNavigate } from "@tanstack/react-router";

import { useCurrentUser } from "@/auth/hooks/useCurrentUser";
import { useLogout } from "@/auth/hooks/useLogout";
import { Button } from "@/components/ui/button";

// The admin dashboard shell — the _authenticated index page. A placeholder
// header + sign-out; per-entity admin pages land in M1.2.
export function AdminShellPage() {
  const { data: user } = useCurrentUser();
  const navigate = useNavigate();
  const logout = useLogout();

  function handleSignOut() {
    logout.mutate({}, { onSettled: () => navigate({ to: "/login" }) });
  }

  return (
    <main className="p-8">
      <header className="flex items-baseline justify-between border-b border-border pb-4">
        <h1 className="text-sm font-medium">sca-tracker — admin</h1>
        <div className="flex items-center gap-3">
          <span className="text-xs text-muted-foreground">{user?.username ?? "—"}</span>
          <Button variant="outline" size="sm" onClick={handleSignOut} disabled={logout.isPending}>
            <SignOutIcon />
            {logout.isPending ? "Signing out…" : "Sign out"}
          </Button>
        </div>
      </header>
      <section className="mt-6 text-xs text-muted-foreground">
        <p>M1.1 auth shell online. Per-entity admin pages land in M1.2.</p>
      </section>
    </main>
  );
}
