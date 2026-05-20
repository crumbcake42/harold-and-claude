// Auth API barrel — the single import surface for auth data access.
//
// loginMutation / logoutMutation are thin re-exports of the generated
// TanStack Query mutation helpers under domain-operation names. The
// current-user query is hand-written (see ./currentUser).

export {
  loginAuthLoginPostMutation as loginMutation,
  logoutAuthLogoutPostMutation as logoutMutation,
} from "@/api/generated/@tanstack/react-query.gen";

export { currentUserQueryKey, currentUserQueryOptions } from "./currentUser";
