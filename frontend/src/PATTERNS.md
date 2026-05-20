# Frontend Patterns

Conventions for the `sca-tracker` frontend. **Read before building any new
feature.** Established in Step 2.1b — ADR-0064 (architecture) and ADR-0065
(UI/form stack).

This document describes the steady-state conventions. Entity-abstraction
patterns (`EntityListPage`, `useEntityForm`, `DataTable`, comboboxes) are
deliberately **not** here — they are extracted just-in-time when a second
consumer appears, not invented up front.

---

## Four-layer architecture

```
routes/  →  pages/  →  features/*  →  components/, hooks/, fields/, lib/
```

| Layer             | Location                                                  | Responsibility                                                                       |
| ----------------- | --------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| Routes            | `src/routes/`                                             | TanStack Router file-based config only — path, `loader`, `beforeLoad`, `validateSearch`. |
| Pages             | `src/pages/<route>/`                                      | URL-bound compositions. Own `getRouteApi`, URL↔state wiring, loader-data consumption. |
| Features          | `src/features/<domain>/`                                  | Routing-agnostic domain components (props in, callbacks out) + per-domain API wrappers. |
| Shared primitives | `src/components/`, `src/hooks/`, `src/fields/`, `src/lib/` | Generic, domain-free building blocks.                                                |

**Direction is strictly one-way.** Features never import from `pages/` or
`routes/`. Pages use `getRouteApi('/path')` and never `import { Route }` from a
route file. Routes import only from `@/pages/` (and `@/auth/`).

`src/auth/` is a deliberate cross-cutting exception — see Routing policy.

Enforced by `no-restricted-imports` in `eslint.config.js`. The `features/` and
`pages/` rules are active; the `routes/` rule lands in Step 2.1b-B, once the
M1.1 auth routes are ported off their direct `@/api/generated/` imports.

---

## API layer

The generated OpenAPI client lives in `src/api/generated/`. **It is committed
and regenerated** — `pnpm gen-api` (or `just gen-openapi`) wipes and rewrites
that directory from `contracts/openapi.json`; never hand-edit it, and CI fails
on drift. Hand-written API code (`src/api/configure.ts`) lives in `src/api/`
but **outside** `generated/`, so regeneration leaves it intact.

### Per-feature API wrappers

Every feature that talks to the backend owns
`src/features/<domain>/api/<domain>.ts`. Feature components and pages import
query/mutation helpers from that file only.

```ts
// features/employees/api/employees.ts  (illustrative — employees land in M1.2)
export {
  listEmployeesEmployeesGetOptions as listEmployeesOptions,
  listEmployeesEmployeesGetQueryKey as listEmployeesQueryKey,
} from "@/api/generated/@tanstack/react-query.gen";
```

**Rules:**

- Feature _components_ and _pages_ never import from `@/api/generated/sdk.gen`
  or `@/api/generated/@tanstack/**` directly.
- Feature _`api/`_ wrapper files are the exception — they are the bridge to the
  generated layer.
- Wrappers use domain-operation names (`listEmployeesOptions`), not the
  generated HTTP-path names (`listEmployeesEmployeesGetOptions`).
- Wrappers are added just-in-time (when first used), not pre-mapped.
- `src/auth/` and `src/lib/` are exempt and may import `@/api/generated/`
  directly.

---

## Types policy

Any interface representing a backend payload **must** be imported from
`@/api/generated/types.gen`. If a type is missing or a generated function
returns `unknown`, that is a backend bug — fix the FastAPI response model and
regenerate. Do not hand-roll the type. `types.gen` imports are allowed in every
layer (the ESLint restriction covers only `sdk.gen` and the `@tanstack`
helpers).

---

## Routing policy

- `/login` is the only public route. Everything else lives under
  `_authenticated/`.
- `_authenticated.tsx`'s `beforeLoad` validates the session via
  `queryClient.ensureQueryData(currentUserQueryOptions())`; on miss it throws
  `redirect({ to: '/login' })`.
- Auth is **cookie-session**, not token-based: an `httpOnly` session cookie
  with `credentials: 'include'` (set in `src/api/configure.ts`). There is no
  token store and no 401 interceptor — ADR-0063 records why both were rejected.
- The login mutation primes the cache with `queryClient.setQueryData(...)`
  before navigating — **not** `invalidateQueries`. See ADR-0063.
- Pages read typed search/loader data via `getRouteApi('/path')`, never by
  importing `Route` from a route file (that creates a circular dependency).

`src/auth/` holds the cross-cutting current-user query
(`currentUserQueryOptions`, `useCurrentUser`) consumed by the route guard. It
sits outside the feature layer because route files must reach it without
violating the one-way rule.

---

## UI components

`src/components/ui/` holds shadcn/ui primitives in the **`radix-lyra`** style
(ADR-0065). They are vendored — added via the shadcn CLI, ESLint-ignored, and
not subject to project lint conventions. Add new primitives just-in-time.

`radix-lyra` has **no `form` component** — see the Form pattern below.

Icons: Phosphor (`@phosphor-icons/react`), using the `*Icon`-suffixed names
(`SignOutIcon`, not the deprecated bare `SignOut`).

---

## Form pattern

- Schema-first with Zod; derive from generated types where possible, manual
  Zod only for cross-field rules.
- `react-hook-form` with `standardSchemaResolver` from
  `@hookform/resolvers/standard-schema` — **not** `zodResolver`.
- Compose with `Field` / `FieldLabel` / `FieldError` / `FieldGroup` from
  `@/components/ui/field` (radix-lyra has no `form` component).
- Type submit-handler events as `SubmitEvent` — `FormEvent` / `FormEventHandler`
  are deprecated in `@types/react` 19.

---

## `src/fields/`

Form-primitive-adjacent components (comboboxes, date pickers, autocompletes),
and any form component shared by ≥2 features, go in `src/fields/` — conceptually
part of the form-primitive layer alongside `Input` and `Field`. A component used
inside only one feature stays in `src/features/<domain>/components/`. Empty
until M1.2 introduces the first shared field.

---

## Testing

- Runner: vitest with the jsdom environment. `pnpm test` runs once.
- Test files are `*.test.tsx` (or `.test.ts`) siblings, colocated with the code
  they cover. `src/test/` holds infrastructure only — setup, render helpers.
- Coverage concentrates where logic lives: `lib/` utilities, `hooks/`, and
  feature components (server-error UX, non-obvious invariants). Pages are thin
  compositions and rarely warrant their own tests. Visual states belong in
  Storybook, not in a parallel vitest matrix.

---

## Storybook

- Stories are `*.stories.tsx` siblings — the same colocation as tests.
- `pnpm storybook` (dev server), `pnpm build-storybook` (static build).
- A shared component gets a story in the same session it is built.
