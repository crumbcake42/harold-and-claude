// Extracts a human-readable message from a rejected API call.
//
// The backend reports every dispatcher rejection as `{ detail: "..." }`
// (see backend `error_handlers.py`); the generated client throws that body
// when `throwOnError` is set. A 422 carries `detail` as a structured
// array instead — not useful to surface verbatim, so it falls through to
// the caller-supplied fallback.
export function apiErrorMessage(error: unknown, fallback: string): string {
  if (error && typeof error === "object" && "detail" in error) {
    const { detail } = error as { detail: unknown };
    if (typeof detail === "string" && detail.length > 0) {
      return detail;
    }
  }
  return fallback;
}
