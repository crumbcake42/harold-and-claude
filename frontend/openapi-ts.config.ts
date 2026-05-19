import { defineConfig } from "@hey-api/openapi-ts";

export default defineConfig({
  input: "../contracts/openapi.json",
  output: {
    path: "src/api",
    postProcess: ["prettier"],
  },
  plugins: [
    "@hey-api/client-fetch",
    "@hey-api/schemas",
    "@hey-api/sdk",
    "@hey-api/typescript",
    "@tanstack/react-query",
  ],
});
