// For more info, see https://github.com/storybookjs/eslint-plugin-storybook#configuration-flat-config-format
import storybook from "eslint-plugin-storybook";

import js from "@eslint/js";
import globals from "globals";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import tseslint from "typescript-eslint";
import prettierRecommended from "eslint-plugin-prettier/recommended";
import { defineConfig, globalIgnores } from "eslint/config";

export default defineConfig([
  globalIgnores([
    "dist",
    "src/routeTree.gen.ts",
    "src/api/generated/**",
    "src/components/ui/**",
    "storybook-static",
  ]),
  {
    files: ["**/*.{ts,tsx}"],
    extends: [
      js.configs.recommended,
      tseslint.configs.recommended,
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      globals: globals.browser,
    },
  },
  ...storybook.configs["flat/recommended"],
  prettierRecommended,
  {
    files: ["src/routes/**/*.{ts,tsx}"],
    rules: {
      "react-refresh/only-export-components": "off",
    },
  },
  // --- Four-layer architecture enforcement (ADR-0064) ---
  // Direction is one-way: routes -> pages -> features -> components/hooks/fields/lib.
  // Feature components/hooks must not reach into routing layers or bypass the
  // per-feature api/ wrapper. Feature api/ wrappers are exempt — they ARE the
  // bridge to @/api/generated/. types.gen is allowed everywhere (types policy);
  // only sdk.gen and the @tanstack query helpers are restricted.
  {
    files: ["src/features/*/components/**", "src/features/*/hooks/**"],
    rules: {
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              group: ["**/pages/**", "**/routes/**"],
              message: "Features are routing-agnostic — do not import from pages/ or routes/.",
            },
            {
              group: ["**/api/generated/sdk.gen*", "**/api/generated/@tanstack/**"],
              message: "Import from @/features/<domain>/api/ instead of @/api/generated/ directly.",
            },
          ],
        },
      ],
    },
  },
  // Pages compose features; they must not bypass the feature api/ wrapper layer.
  {
    files: ["src/pages/**"],
    rules: {
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              group: ["**/api/generated/sdk.gen*", "**/api/generated/@tanstack/**"],
              message: "Import from @/features/<domain>/api/ instead of @/api/generated/ directly.",
            },
          ],
        },
      ],
    },
  },
  // NOTE: the routes/ layering rule (routes import only from @/pages/ and
  // @/auth/) lands in Step 2.1b-B, once the M1.1 auth route files are ported
  // off their direct @/api/generated/ imports. Adding it now would fail lint
  // on the not-yet-ported login / _authenticated routes.
]);
