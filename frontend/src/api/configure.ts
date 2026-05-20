// API client configuration.
//
// Hand-written — lives in src/api/ alongside the generated client, but NOT
// inside src/api/generated/. openapi-ts wipes and regenerates only its
// output dir (src/api/generated/, per openapi-ts.config.ts); files in
// src/api/ outside that subdir are hand-authored and survive regeneration.
//
// The generated client (src/api/generated/client.gen.ts) ships with a
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
// redirect logic in the API client risks recursive 401 -> /auth/me -> 401
// loops and obscures the auth contract. See ADR-0063.

import { client } from "./generated/client.gen";

export function configureApiClient(): void {
  const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
  client.setConfig({
    baseUrl,
    credentials: "include",
  });
}
