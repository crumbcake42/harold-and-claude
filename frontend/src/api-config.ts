// API client configuration for the M1.1 auth substrate.
//
// This file is hand-written and MUST live outside src/api/ -- openapi-ts
// wipes and regenerates that entire directory on every `just gen-openapi`,
// which would delete this file and break the contract-drift CI check.
//
// The openapi-ts generated client (src/api/client.gen.ts) ships with a
// default Config; we override at app startup with:
//
//   - baseUrl: backend origin (env-driven; defaults to local dev port)
//   - credentials: "include" so the SameSite=Lax session cookie is sent
//     on every request (load-bearing for the auth round-trip; without it
//     the browser drops the cookie cross-origin even with CORS)
//
// 401 handling is intentionally NOT done via an interceptor here -- the
// _authenticated route's beforeLoad reads the useCurrentUser query and
// throws a redirect on miss, which is the single canonical path. Putting
// redirect logic in the API client risks recursive 401 → /auth/me → 401
// loops and obscures the auth contract.

import { client } from "./api/client.gen";

export function configureApiClient(): void {
  const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
  client.setConfig({
    baseUrl,
    credentials: "include",
  });
}
