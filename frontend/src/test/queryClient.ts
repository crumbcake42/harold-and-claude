import { QueryClient } from "@tanstack/react-query";

/** A QueryClient for tests — retries and caching disabled for determinism. */
export function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
      mutations: { retry: false },
    },
  });
}
