import { defineConfig } from "oxlint";

export default defineConfig({
    plugins: ["typescript", "unicorn", "oxc"],

    categories: {
        correctness: "error",
        suspicious: "warn",
        pedantic: "off",
    },

    rules: {
        "eslint/no-unused-vars": "error",
        "no-alert": "error",
        "no-console": "error",
        "oxc/approx-constant": "warn",
        "no-plusplus": ["error", { allowForLoopAfterthoughts: true }],
        "eslint/prefer-const": ["error", { destructuring: "any" }],
    },

    overrides: [
        {
            files: ["scripts/*.js"],
            rules: {
                "no-console": "off",
            },
        },
        {
            files: ["**/*.{ts,tsx}"],
            plugins: ["typescript"],
            rules: {
                "typescript/no-explicit-any": "error",
            },
        },
        {
            files: ["**/test/**"],
            plugins: ["jest"],
            env: {
                jest: true,
            },
            rules: {
                "jest/no-disabled-tests": "off",
            },
        },
    ],

    env: {
        builtin: true,
    },

    options: {
        typeAware: true,
        typeCheck: true,
        maxWarnings: 10,
    },
});
