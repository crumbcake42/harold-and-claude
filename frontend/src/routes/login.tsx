import { useState, type SubmitEvent } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createFileRoute, useNavigate } from "@tanstack/react-router";

import { loginAuthLoginPost, type LoginRequest } from "../api/generated";
import { currentUserQueryKey } from "../hooks/useCurrentUser";

export const Route = createFileRoute("/login")({
  component: LoginPage,
});

function LoginPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const loginMutation = useMutation({
    mutationFn: async (body: LoginRequest) => {
      const response = await loginAuthLoginPost({ body, throwOnError: false });
      if (response.error) {
        throw new Error("invalid credentials");
      }
      return response.data;
    },
    onSuccess: (data) => {
      // Seed the cache with the Caller the login response already returned.
      // invalidateQueries here would defeat us: with no active subscriber to
      // ['auth', 'me'] on the /login page, invalidate marks stale but does
      // not refetch, and _authenticated's beforeLoad then reads the stale
      // null and bounces us back to /login.
      if (data) {
        queryClient.setQueryData(currentUserQueryKey, data);
      }
      navigate({ to: "/" });
    },
  });

  const handleSubmit = (e: SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();
    loginMutation.mutate({ username, password });
  };

  return (
    <main style={{ maxWidth: 320, margin: "4rem auto", fontFamily: "system-ui" }}>
      <h1>sca-tracker</h1>
      <form onSubmit={handleSubmit}>
        <label style={{ display: "block", marginBottom: "0.75rem" }}>
          username
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
            required
            style={{ display: "block", width: "100%", padding: "0.5rem" }}
          />
        </label>
        <label style={{ display: "block", marginBottom: "0.75rem" }}>
          password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
            style={{ display: "block", width: "100%", padding: "0.5rem" }}
          />
        </label>
        <button type="submit" disabled={loginMutation.isPending} style={{ padding: "0.5rem 1rem" }}>
          {loginMutation.isPending ? "signing in…" : "sign in"}
        </button>
        {loginMutation.isError ? (
          <p style={{ color: "crimson", marginTop: "0.75rem" }} role="alert">
            invalid credentials
          </p>
        ) : null}
      </form>
    </main>
  );
}
