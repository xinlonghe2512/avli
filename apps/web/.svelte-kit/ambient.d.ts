
// this file is generated — do not edit it


/// <reference types="@sveltejs/kit" />

/**
 * This module provides access to environment variables that are injected _statically_ into your bundle at build time and are limited to _private_ access.
 * 
 * |         | Runtime                                                                    | Build time                                                               |
 * | ------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
 * | Private | [`$env/dynamic/private`](https://svelte.dev/docs/kit/$env-dynamic-private) | [`$env/static/private`](https://svelte.dev/docs/kit/$env-static-private) |
 * | Public  | [`$env/dynamic/public`](https://svelte.dev/docs/kit/$env-dynamic-public)   | [`$env/static/public`](https://svelte.dev/docs/kit/$env-static-public)   |
 * 
 * Static environment variables are [loaded by Vite](https://vitejs.dev/guide/env-and-mode.html#env-files) from `.env` files and `process.env` at build time and then statically injected into your bundle at build time, enabling optimisations like dead code elimination.
 * 
 * **_Private_ access:**
 * 
 * - This module cannot be imported into client-side code
 * - This module only includes variables that _do not_ begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) _and do_ start with [`config.kit.env.privatePrefix`](https://svelte.dev/docs/kit/configuration#env) (if configured)
 * 
 * For example, given the following build time environment:
 * 
 * ```env
 * ENVIRONMENT=production
 * PUBLIC_BASE_URL=http://site.com
 * ```
 * 
 * With the default `publicPrefix` and `privatePrefix`:
 * 
 * ```ts
 * import { ENVIRONMENT, PUBLIC_BASE_URL } from '$env/static/private';
 * 
 * console.log(ENVIRONMENT); // => "production"
 * console.log(PUBLIC_BASE_URL); // => throws error during build
 * ```
 * 
 * The above values will be the same _even if_ different values for `ENVIRONMENT` or `PUBLIC_BASE_URL` are set at runtime, as they are statically replaced in your code with their build time values.
 */
declare module '$env/static/private' {
	export const ALLOWED_ORIGINS: string;
	export const ALLOY_PORT: string;
	export const ANDROID_HOME: string;
	export const ANDROID_SDK_ROOT: string;
	export const API_PREFIX: string;
	export const BUNDLED_DEBUGPY_PATH: string;
	export const CACHE_DB: string;
	export const CACHE_MAX_CONNECTIONS: string;
	export const CACHE_PASSWORD: string;
	export const CACHE_PORT: string;
	export const CACHE_TTL_SECONDS: string;
	export const CADVISOR_PORT: string;
	export const CHECKPOINT_TABLES: string;
	export const CHROME_DESKTOP: string;
	export const CHROME_EXECUTABLE: string;
	export const CLAUDE_CODE_SSE_PORT: string;
	export const CLOUDSDK_ROOT_DIR: string;
	export const COLORTERM: string;
	export const COPILOT_DEBUG_NONCE: string;
	export const CUDA_DISABLE_PERF_BOOST: string;
	export const CUDA_PATH: string;
	export const DBUS_SESSION_BUS_ADDRESS: string;
	export const DEBUG: string;
	export const DEBUGINFOD_URLS: string;
	export const DESCRIPTION: string;
	export const DESKTOP_SESSION: string;
	export const DISPLAY: string;
	export const ENVIRONMENT: string;
	export const EVALUATION_API_URL: string;
	export const EVALUATION_LLM: string;
	export const EVALUATION_SLEEP_TIME: string;
	export const FC_FONTATIONS: string;
	export const FLUTTER_ADB_PATH: string;
	export const GDK_BACKEND: string;
	export const GIT_ASKPASS: string;
	export const GOOGLE_CLOUD_SDK_HOME: string;
	export const GRADLE_HOME: string;
	export const GRAFANA_PORT: string;
	export const GRAFANA_SECURITY_ADMIN_PASSWORD: string;
	export const GRAFANA_SECURITY_ADMIN_USER: string;
	export const GTK2_RC_FILES: string;
	export const GTK_RC_FILES: string;
	export const HOME: string;
	export const ICEAUTHORITY: string;
	export const INIT_CWD: string;
	export const INVOCATION_ID: string;
	export const JOURNAL_STREAM: string;
	export const JS_RUNTIME_NAME: string;
	export const JS_RUNTIME_VERSION: string;
	export const JWT_ACCESS_TOKEN_EXPIRE_DAYS: string;
	export const JWT_ALGORITHM: string;
	export const JWT_SECRET_KEY: string;
	export const KDE_APPLICATIONS_AS_SCOPE: string;
	export const KDE_FULL_SESSION: string;
	export const KDE_SESSION_UID: string;
	export const KDE_SESSION_VERSION: string;
	export const KNOWLEDGE_BASE_CHUNK_OVERLAP: string;
	export const KNOWLEDGE_BASE_CHUNK_SIZE: string;
	export const KNOWLEDGE_BASE_COLLECTION_NAME: string;
	export const KNOWLEDGE_BASE_EMBEDDING_MODEL: string;
	export const KNOWLEDGE_BASE_PORT: string;
	export const KNOWLEDGE_BASE_URL: string;
	export const LANG: string;
	export const LANGFUSE_HOST: string;
	export const LANGFUSE_PUBLIC_KEY: string;
	export const LANGFUSE_SECRET_KEY: string;
	export const LANGFUSE_TRACING_ENABLED: string;
	export const LC_ADDRESS: string;
	export const LC_IDENTIFICATION: string;
	export const LC_MEASUREMENT: string;
	export const LC_MONETARY: string;
	export const LC_NAME: string;
	export const LC_NUMERIC: string;
	export const LC_PAPER: string;
	export const LC_TELEPHONE: string;
	export const LC_TIME: string;
	export const LLM_CONTEXT_BUDGET: string;
	export const LLM_MAX_CALL_RETRIES: string;
	export const LLM_MODEL: string;
	export const LLM_TEMPERATURE: string;
	export const LLM_TOTAL_TIMEOUT: string;
	export const LOGNAME: string;
	export const LOG_DIR: string;
	export const LOG_FORMAT: string;
	export const LOG_LEVEL: string;
	export const LOKI_PORT: string;
	export const LONG_TERM_MEMORY_COLLECTION_NAME: string;
	export const LONG_TERM_MEMORY_EMBEDDING_MODEL: string;
	export const LONG_TERM_MEMORY_MODEL: string;
	export const MAIL: string;
	export const MANAGERPID: string;
	export const MANAGERPIDFDID: string;
	export const MANPAGER: string;
	export const MANROFFOPT: string;
	export const MEM0_KEY: string;
	export const MEMORY_PRESSURE_WATCH: string;
	export const MEMORY_PRESSURE_WRITE: string;
	export const MODEL_PROVIDER_API_BASE: string;
	export const MOTD_SHOWN: string;
	export const NODE: string;
	export const NODE_PACKAGE_MANAGER: string;
	export const NODE_PATH: string;
	export const NO_AT_BRIDGE: string;
	export const NVCC_CCBIN: string;
	export const PAM_KWALLET5_LOGIN: string;
	export const PATH: string;
	export const PNPM_SCRIPT_SRC_DIR: string;
	export const POSTGRES_DB: string;
	export const POSTGRES_HOST: string;
	export const POSTGRES_MAX_OVERFLOW: string;
	export const POSTGRES_PASSWORD: string;
	export const POSTGRES_POOL_SIZE: string;
	export const POSTGRES_PORT: string;
	export const POSTGRES_USER: string;
	export const PROFILING_DIR: string;
	export const PROFILING_THRESHOLD_SECONDS: string;
	export const PROJECT_NAME: string;
	export const PROMETHEUS_PORT: string;
	export const PWD: string;
	export const PYDEVD_DISABLE_FILE_VALIDATION: string;
	export const PYTHONSTARTUP: string;
	export const PYTHON_BASIC_REPL: string;
	export const QT_WAYLAND_RECONNECT: string;
	export const SESSION_MANAGER: string;
	export const SESSION_NAMING_ENABLED: string;
	export const SHELL: string;
	export const SHLVL: string;
	export const SYSTEMD_EXEC_PID: string;
	export const TERM: string;
	export const TERM_PROGRAM: string;
	export const TERM_PROGRAM_VERSION: string;
	export const USER: string;
	export const VERSION: string;
	export const VIRTUAL_ENV: string;
	export const VIRTUAL_ENV_DISABLE_PROMPT: string;
	export const VIRTUAL_ENV_PROMPT: string;
	export const VP_HOME: string;
	export const VP_PATH_INJECTED_TOOLS: string;
	export const VP_VERSION: string;
	export const VSCODE_DEBUGPY_ADAPTER_ENDPOINTS: string;
	export const VSCODE_GIT_ASKPASS_EXTRA_ARGS: string;
	export const VSCODE_GIT_ASKPASS_MAIN: string;
	export const VSCODE_GIT_ASKPASS_NODE: string;
	export const VSCODE_GIT_IPC_HANDLE: string;
	export const VSCODE_INJECTION: string;
	export const VSCODE_PYTHON_AUTOACTIVATE_GUARD: string;
	export const VSSCRIPT_PATH: string;
	export const WAYLAND_DISPLAY: string;
	export const XAUTHORITY: string;
	export const XDG_CONFIG_DIRS: string;
	export const XDG_CURRENT_DESKTOP: string;
	export const XDG_MENU_PREFIX: string;
	export const XDG_RUNTIME_DIR: string;
	export const XDG_SEAT: string;
	export const XDG_SEAT_PATH: string;
	export const XDG_SESSION_CLASS: string;
	export const XDG_SESSION_DESKTOP: string;
	export const XDG_SESSION_ID: string;
	export const XDG_SESSION_PATH: string;
	export const XDG_SESSION_TYPE: string;
	export const XDG_VTNR: string;
	export const XKB_DEFAULT_LAYOUT: string;
	export const _JAVA_AWT_WM_NONREPARENTING: string;
	export const _OLD_VIRTUAL_PATH: string;
	export const npm_config_user_agent: string;
	export const npm_execpath: string;
	export const npm_lifecycle_event: string;
	export const npm_lifecycle_script: string;
	export const npm_node_execpath: string;
	export const npm_package_json: string;
	export const npm_package_name: string;
	export const npm_package_version: string;
	export const pnpm_config_verify_deps_before_run: string;
	export const NODE_ENV: string;
	export const PW_EXPERIMENTAL_SERVICE_WORKER_NETWORK_EVENTS: string;
}

/**
 * This module provides access to environment variables that are injected _statically_ into your bundle at build time and are _publicly_ accessible.
 * 
 * |         | Runtime                                                                    | Build time                                                               |
 * | ------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
 * | Private | [`$env/dynamic/private`](https://svelte.dev/docs/kit/$env-dynamic-private) | [`$env/static/private`](https://svelte.dev/docs/kit/$env-static-private) |
 * | Public  | [`$env/dynamic/public`](https://svelte.dev/docs/kit/$env-dynamic-public)   | [`$env/static/public`](https://svelte.dev/docs/kit/$env-static-public)   |
 * 
 * Static environment variables are [loaded by Vite](https://vitejs.dev/guide/env-and-mode.html#env-files) from `.env` files and `process.env` at build time and then statically injected into your bundle at build time, enabling optimisations like dead code elimination.
 * 
 * **_Public_ access:**
 * 
 * - This module _can_ be imported into client-side code
 * - **Only** variables that begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) (which defaults to `PUBLIC_`) are included
 * 
 * For example, given the following build time environment:
 * 
 * ```env
 * ENVIRONMENT=production
 * PUBLIC_BASE_URL=http://site.com
 * ```
 * 
 * With the default `publicPrefix` and `privatePrefix`:
 * 
 * ```ts
 * import { ENVIRONMENT, PUBLIC_BASE_URL } from '$env/static/public';
 * 
 * console.log(ENVIRONMENT); // => throws error during build
 * console.log(PUBLIC_BASE_URL); // => "http://site.com"
 * ```
 * 
 * The above values will be the same _even if_ different values for `ENVIRONMENT` or `PUBLIC_BASE_URL` are set at runtime, as they are statically replaced in your code with their build time values.
 */
declare module '$env/static/public' {
	
}

/**
 * This module provides access to environment variables set _dynamically_ at runtime and that are limited to _private_ access.
 * 
 * |         | Runtime                                                                    | Build time                                                               |
 * | ------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
 * | Private | [`$env/dynamic/private`](https://svelte.dev/docs/kit/$env-dynamic-private) | [`$env/static/private`](https://svelte.dev/docs/kit/$env-static-private) |
 * | Public  | [`$env/dynamic/public`](https://svelte.dev/docs/kit/$env-dynamic-public)   | [`$env/static/public`](https://svelte.dev/docs/kit/$env-static-public)   |
 * 
 * Dynamic environment variables are defined by the platform you're running on. For example if you're using [`adapter-node`](https://github.com/sveltejs/kit/tree/main/packages/adapter-node) (or running [`vite preview`](https://svelte.dev/docs/kit/cli)), this is equivalent to `process.env`.
 * 
 * **_Private_ access:**
 * 
 * - This module cannot be imported into client-side code
 * - This module includes variables that _do not_ begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) _and do_ start with [`config.kit.env.privatePrefix`](https://svelte.dev/docs/kit/configuration#env) (if configured)
 * 
 * > [!NOTE] In `dev`, `$env/dynamic` includes environment variables from `.env`. In `prod`, this behavior will depend on your adapter.
 * 
 * > [!NOTE] To get correct types, environment variables referenced in your code should be declared (for example in an `.env` file), even if they don't have a value until the app is deployed:
 * >
 * > ```env
 * > MY_FEATURE_FLAG=
 * > ```
 * >
 * > You can override `.env` values from the command line like so:
 * >
 * > ```sh
 * > MY_FEATURE_FLAG="enabled" npm run dev
 * > ```
 * 
 * For example, given the following runtime environment:
 * 
 * ```env
 * ENVIRONMENT=production
 * PUBLIC_BASE_URL=http://site.com
 * ```
 * 
 * With the default `publicPrefix` and `privatePrefix`:
 * 
 * ```ts
 * import { env } from '$env/dynamic/private';
 * 
 * console.log(env.ENVIRONMENT); // => "production"
 * console.log(env.PUBLIC_BASE_URL); // => undefined
 * ```
 */
declare module '$env/dynamic/private' {
	export const env: {
		ALLOWED_ORIGINS: string;
		ALLOY_PORT: string;
		ANDROID_HOME: string;
		ANDROID_SDK_ROOT: string;
		API_PREFIX: string;
		BUNDLED_DEBUGPY_PATH: string;
		CACHE_DB: string;
		CACHE_MAX_CONNECTIONS: string;
		CACHE_PASSWORD: string;
		CACHE_PORT: string;
		CACHE_TTL_SECONDS: string;
		CADVISOR_PORT: string;
		CHECKPOINT_TABLES: string;
		CHROME_DESKTOP: string;
		CHROME_EXECUTABLE: string;
		CLAUDE_CODE_SSE_PORT: string;
		CLOUDSDK_ROOT_DIR: string;
		COLORTERM: string;
		COPILOT_DEBUG_NONCE: string;
		CUDA_DISABLE_PERF_BOOST: string;
		CUDA_PATH: string;
		DBUS_SESSION_BUS_ADDRESS: string;
		DEBUG: string;
		DEBUGINFOD_URLS: string;
		DESCRIPTION: string;
		DESKTOP_SESSION: string;
		DISPLAY: string;
		ENVIRONMENT: string;
		EVALUATION_API_URL: string;
		EVALUATION_LLM: string;
		EVALUATION_SLEEP_TIME: string;
		FC_FONTATIONS: string;
		FLUTTER_ADB_PATH: string;
		GDK_BACKEND: string;
		GIT_ASKPASS: string;
		GOOGLE_CLOUD_SDK_HOME: string;
		GRADLE_HOME: string;
		GRAFANA_PORT: string;
		GRAFANA_SECURITY_ADMIN_PASSWORD: string;
		GRAFANA_SECURITY_ADMIN_USER: string;
		GTK2_RC_FILES: string;
		GTK_RC_FILES: string;
		HOME: string;
		ICEAUTHORITY: string;
		INIT_CWD: string;
		INVOCATION_ID: string;
		JOURNAL_STREAM: string;
		JS_RUNTIME_NAME: string;
		JS_RUNTIME_VERSION: string;
		JWT_ACCESS_TOKEN_EXPIRE_DAYS: string;
		JWT_ALGORITHM: string;
		JWT_SECRET_KEY: string;
		KDE_APPLICATIONS_AS_SCOPE: string;
		KDE_FULL_SESSION: string;
		KDE_SESSION_UID: string;
		KDE_SESSION_VERSION: string;
		KNOWLEDGE_BASE_CHUNK_OVERLAP: string;
		KNOWLEDGE_BASE_CHUNK_SIZE: string;
		KNOWLEDGE_BASE_COLLECTION_NAME: string;
		KNOWLEDGE_BASE_EMBEDDING_MODEL: string;
		KNOWLEDGE_BASE_PORT: string;
		KNOWLEDGE_BASE_URL: string;
		LANG: string;
		LANGFUSE_HOST: string;
		LANGFUSE_PUBLIC_KEY: string;
		LANGFUSE_SECRET_KEY: string;
		LANGFUSE_TRACING_ENABLED: string;
		LC_ADDRESS: string;
		LC_IDENTIFICATION: string;
		LC_MEASUREMENT: string;
		LC_MONETARY: string;
		LC_NAME: string;
		LC_NUMERIC: string;
		LC_PAPER: string;
		LC_TELEPHONE: string;
		LC_TIME: string;
		LLM_CONTEXT_BUDGET: string;
		LLM_MAX_CALL_RETRIES: string;
		LLM_MODEL: string;
		LLM_TEMPERATURE: string;
		LLM_TOTAL_TIMEOUT: string;
		LOGNAME: string;
		LOG_DIR: string;
		LOG_FORMAT: string;
		LOG_LEVEL: string;
		LOKI_PORT: string;
		LONG_TERM_MEMORY_COLLECTION_NAME: string;
		LONG_TERM_MEMORY_EMBEDDING_MODEL: string;
		LONG_TERM_MEMORY_MODEL: string;
		MAIL: string;
		MANAGERPID: string;
		MANAGERPIDFDID: string;
		MANPAGER: string;
		MANROFFOPT: string;
		MEM0_KEY: string;
		MEMORY_PRESSURE_WATCH: string;
		MEMORY_PRESSURE_WRITE: string;
		MODEL_PROVIDER_API_BASE: string;
		MOTD_SHOWN: string;
		NODE: string;
		NODE_PACKAGE_MANAGER: string;
		NODE_PATH: string;
		NO_AT_BRIDGE: string;
		NVCC_CCBIN: string;
		PAM_KWALLET5_LOGIN: string;
		PATH: string;
		PNPM_SCRIPT_SRC_DIR: string;
		POSTGRES_DB: string;
		POSTGRES_HOST: string;
		POSTGRES_MAX_OVERFLOW: string;
		POSTGRES_PASSWORD: string;
		POSTGRES_POOL_SIZE: string;
		POSTGRES_PORT: string;
		POSTGRES_USER: string;
		PROFILING_DIR: string;
		PROFILING_THRESHOLD_SECONDS: string;
		PROJECT_NAME: string;
		PROMETHEUS_PORT: string;
		PWD: string;
		PYDEVD_DISABLE_FILE_VALIDATION: string;
		PYTHONSTARTUP: string;
		PYTHON_BASIC_REPL: string;
		QT_WAYLAND_RECONNECT: string;
		SESSION_MANAGER: string;
		SESSION_NAMING_ENABLED: string;
		SHELL: string;
		SHLVL: string;
		SYSTEMD_EXEC_PID: string;
		TERM: string;
		TERM_PROGRAM: string;
		TERM_PROGRAM_VERSION: string;
		USER: string;
		VERSION: string;
		VIRTUAL_ENV: string;
		VIRTUAL_ENV_DISABLE_PROMPT: string;
		VIRTUAL_ENV_PROMPT: string;
		VP_HOME: string;
		VP_PATH_INJECTED_TOOLS: string;
		VP_VERSION: string;
		VSCODE_DEBUGPY_ADAPTER_ENDPOINTS: string;
		VSCODE_GIT_ASKPASS_EXTRA_ARGS: string;
		VSCODE_GIT_ASKPASS_MAIN: string;
		VSCODE_GIT_ASKPASS_NODE: string;
		VSCODE_GIT_IPC_HANDLE: string;
		VSCODE_INJECTION: string;
		VSCODE_PYTHON_AUTOACTIVATE_GUARD: string;
		VSSCRIPT_PATH: string;
		WAYLAND_DISPLAY: string;
		XAUTHORITY: string;
		XDG_CONFIG_DIRS: string;
		XDG_CURRENT_DESKTOP: string;
		XDG_MENU_PREFIX: string;
		XDG_RUNTIME_DIR: string;
		XDG_SEAT: string;
		XDG_SEAT_PATH: string;
		XDG_SESSION_CLASS: string;
		XDG_SESSION_DESKTOP: string;
		XDG_SESSION_ID: string;
		XDG_SESSION_PATH: string;
		XDG_SESSION_TYPE: string;
		XDG_VTNR: string;
		XKB_DEFAULT_LAYOUT: string;
		_JAVA_AWT_WM_NONREPARENTING: string;
		_OLD_VIRTUAL_PATH: string;
		npm_config_user_agent: string;
		npm_execpath: string;
		npm_lifecycle_event: string;
		npm_lifecycle_script: string;
		npm_node_execpath: string;
		npm_package_json: string;
		npm_package_name: string;
		npm_package_version: string;
		pnpm_config_verify_deps_before_run: string;
		NODE_ENV: string;
		PW_EXPERIMENTAL_SERVICE_WORKER_NETWORK_EVENTS: string;
		[key: `PUBLIC_${string}`]: undefined;
		[key: `${string}`]: string | undefined;
	}
}

/**
 * This module provides access to environment variables set _dynamically_ at runtime and that are _publicly_ accessible.
 * 
 * |         | Runtime                                                                    | Build time                                                               |
 * | ------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
 * | Private | [`$env/dynamic/private`](https://svelte.dev/docs/kit/$env-dynamic-private) | [`$env/static/private`](https://svelte.dev/docs/kit/$env-static-private) |
 * | Public  | [`$env/dynamic/public`](https://svelte.dev/docs/kit/$env-dynamic-public)   | [`$env/static/public`](https://svelte.dev/docs/kit/$env-static-public)   |
 * 
 * Dynamic environment variables are defined by the platform you're running on. For example if you're using [`adapter-node`](https://github.com/sveltejs/kit/tree/main/packages/adapter-node) (or running [`vite preview`](https://svelte.dev/docs/kit/cli)), this is equivalent to `process.env`.
 * 
 * **_Public_ access:**
 * 
 * - This module _can_ be imported into client-side code
 * - **Only** variables that begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) (which defaults to `PUBLIC_`) are included
 * 
 * > [!NOTE] In `dev`, `$env/dynamic` includes environment variables from `.env`. In `prod`, this behavior will depend on your adapter.
 * 
 * > [!NOTE] To get correct types, environment variables referenced in your code should be declared (for example in an `.env` file), even if they don't have a value until the app is deployed:
 * >
 * > ```env
 * > MY_FEATURE_FLAG=
 * > ```
 * >
 * > You can override `.env` values from the command line like so:
 * >
 * > ```sh
 * > MY_FEATURE_FLAG="enabled" npm run dev
 * > ```
 * 
 * For example, given the following runtime environment:
 * 
 * ```env
 * ENVIRONMENT=production
 * PUBLIC_BASE_URL=http://example.com
 * ```
 * 
 * With the default `publicPrefix` and `privatePrefix`:
 * 
 * ```ts
 * import { env } from '$env/dynamic/public';
 * console.log(env.ENVIRONMENT); // => undefined, not public
 * console.log(env.PUBLIC_BASE_URL); // => "http://example.com"
 * ```
 * 
 * ```
 * 
 * ```
 */
declare module '$env/dynamic/public' {
	export const env: {
		[key: `PUBLIC_${string}`]: string | undefined;
	}
}
