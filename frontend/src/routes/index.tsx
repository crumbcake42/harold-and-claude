import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  component: HomePage,
});

function HomePage() {
  return (
    <main>
      <h1>sca-tracker</h1>
      <p>M0.1 scaffolding online.</p>
    </main>
  );
}
