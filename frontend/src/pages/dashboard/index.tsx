// The authenticated landing page — the `_authenticated` index route. A
// minimal placeholder for now; it grows into a real dashboard as more of
// the admin surface lands. The navigation is the way into each section.
export function DashboardPage() {
  return (
    <div className="max-w-prose">
      <h1 className="text-lg font-semibold">Admin dashboard</h1>
      <p className="mt-2 text-sm text-muted-foreground">
        Select a section from the navigation to begin.
      </p>
    </div>
  );
}
