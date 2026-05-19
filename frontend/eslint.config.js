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
  globalIgnores(["dist", "src/routeTree.gen.ts", "src/api/**", "storybook-static"]),
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
]);
