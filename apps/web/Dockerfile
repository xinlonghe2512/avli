FROM docker.io/node:24.21.0-trixie-slim AS builder

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

RUN corepack enable && corepack prepare pnpm@12.4.2 --activate

WORKDIR /app

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./
COPY apps/web/package.json apps/web/package.json

RUN pnpm install --frozen-lockfile

COPY apps/web apps/web

WORKDIR /app/apps/web

RUN pnpm build


FROM docker.io/node:24.21.0-trixie-slim

ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=5173

WORKDIR /app

COPY --from=builder /app/apps/web/build ./build
COPY --from=builder /app/apps/web/node_modules ./node_modules
COPY --from=builder /app/apps/web/package.json ./

EXPOSE 5173

CMD [ "node", "build" ]
