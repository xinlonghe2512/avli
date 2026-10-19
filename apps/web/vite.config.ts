import { paraglideVitePlugin } from "@inlang/paraglide-js";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig, lazyPlugins } from "vite-plus";
import { playwright } from "vite-plus/test/browser-playwright";
import { sveltekit } from "@sveltejs/kit/vite";

export default defineConfig({
    fmt: {},
    lint: {
        jsPlugins: [{ name: "vite-plus", specifier: "vite-plus/oxlint-plugin" }],
        rules: { "vite-plus/prefer-vite-plus-imports": "error" },
        options: { typeAware: true, typeCheck: true },
    },
    plugins: lazyPlugins(() => [
        tailwindcss(),
        sveltekit(),
        paraglideVitePlugin({
            project: "./project.inlang",
            outdir: "./src/lib/paraglide",
            emitTsDeclarations: true,
        }),
    ]),
    server: {
        port: 5173,
    },
    test: {
        // Vitest v4 compatibility: preserve mock call history.
        // Remove after tests no longer rely on calls from setup or earlier tests.
        // https://viteplus.dev/guide/vitest-v5#remove-unneeded-compatibility-settings
        // https://vitest.dev/guide/migration/#clearmocks-is-enabled-by-default
        clearMocks: false,
        // Vitest v4 compatibility: keep separate Vite servers for inline projects.
        // Remove when plugins and config hooks can run once for shared projects.
        // https://viteplus.dev/guide/vitest-v5#remove-unneeded-compatibility-settings
        // https://vitest.dev/guide/migration/#inline-projects-share-the-vite-server-by-default
        // sharedViteServer: false,
        expect: {
            requireAssertions: true,
        },
        projects: [
            {
                extends: "./vite.config.ts",
                test: {
                    name: "client",
                    include: ["src/**/*.svelte.{test,spec}.{js,ts}"],
                    exclude: ["src/lib/server/**"],
                    browser: {
                        enabled: true,
                        provider: playwright(),
                        instances: [{ browser: "chromium", headless: true }],
                    },
                },
            },
            {
                extends: "./vite.config.ts",
                test: {
                    name: "server",
                    environment: "node",
                    include: ["src/**/*.{test,spec}.{js,ts}"],
                    exclude: ["src/**/*.svelte.{test,spec}.{js,ts}"],
                },
            },
        ],
    },
});
