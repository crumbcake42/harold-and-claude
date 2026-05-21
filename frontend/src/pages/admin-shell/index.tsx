import { FileTextIcon, HouseIcon, SignOutIcon } from "@phosphor-icons/react";
import { Link, Outlet, useNavigate } from "@tanstack/react-router";

import { useCurrentUser } from "@/auth/hooks/useCurrentUser";
import { useLogout } from "@/auth/hooks/useLogout";
import { Button } from "@/components/ui/button";

// The admin shell — the persistent chrome for every authenticated page.
// It is the component of the `_authenticated` route: the auth guard wraps
// it, and each page renders into the <Outlet/>. Per-entity nav entries are
// added here as features land (Contracts now; the roster batch follows).
const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: HouseIcon },
  { to: "/contracts", label: "Contracts", icon: FileTextIcon },
] as const;

export function AdminShellLayout() {
  const { data: user } = useCurrentUser();
  const navigate = useNavigate();
  const logout = useLogout();

  function handleSignOut() {
    logout.mutate({}, { onSettled: () => navigate({ to: "/login" }) });
  }

  return (
    <div className="flex min-h-screen flex-col">
      <header className="flex items-baseline justify-between border-b border-border px-6 py-3">
        <span className="text-sm font-medium">sca-tracker — admin</span>
        <div className="flex items-center gap-3">
          <span className="text-xs text-muted-foreground">{user?.username ?? "—"}</span>
          <Button variant="outline" size="sm" onClick={handleSignOut} disabled={logout.isPending}>
            <SignOutIcon />
            {logout.isPending ? "Signing out…" : "Sign out"}
          </Button>
        </div>
      </header>
      <div className="flex flex-1">
        <nav className="w-48 shrink-0 border-r border-border p-3">
          <ul className="flex flex-col gap-1">
            {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
              <li key={to}>
                <Link
                  to={to}
                  activeOptions={{ exact: to === "/" }}
                  className="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-muted-foreground hover:bg-muted hover:text-foreground"
                  activeProps={{ className: "bg-muted font-medium text-foreground" }}
                >
                  <Icon />
                  {label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
        <main className="flex-1 p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
