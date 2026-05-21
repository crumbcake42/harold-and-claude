import { useNavigate } from "@tanstack/react-router";
import { toast } from "sonner";

import { LoginForm } from "@/auth/components/LoginForm";
import type { LoginFormValues } from "@/auth/components/LoginForm";
import { useLogin } from "@/auth/hooks/useLogin";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function LoginPage() {
  const navigate = useNavigate();
  const login = useLogin();

  async function onSubmit(values: LoginFormValues) {
    try {
      await login.mutateAsync({ body: values });
      // Post-login lands on the caller's highest accessible dashboard. Only the
      // /admin surface exists today, so this targets /admin/dashboard directly;
      // ADR-0077 records the role-dispatch design.
      await navigate({ to: "/admin/dashboard" });
    } catch {
      // Server-side rejection (bad credentials). Client-side validation is
      // already handled inside LoginForm by the Zod resolver.
      toast.error("Invalid username or password");
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle className="text-center text-sm">sca-tracker</CardTitle>
        </CardHeader>
        <CardContent>
          <LoginForm onSubmit={onSubmit} isPending={login.isPending} />
        </CardContent>
      </Card>
    </div>
  );
}
