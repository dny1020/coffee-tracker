# Multi-stage build for Node.js + TypeScript + Prisma

FROM docker.io/library/node:20-bookworm-slim AS build
WORKDIR /app

COPY package.json package-lock.json ./
COPY tsconfig.json prisma.config.ts ./
COPY prisma ./prisma
COPY src ./src

RUN npm ci --include=dev --no-audit --no-fund
RUN npm run build
RUN npm prune --omit=dev

FROM docker.io/library/node:20-bookworm-slim AS runtime
WORKDIR /app
ENV NODE_ENV=production

COPY --from=build /app/package.json /app/package-lock.json ./
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
COPY --from=build /app/prisma ./prisma
COPY --from=build /app/prisma.config.ts ./prisma.config.ts

EXPOSE 8000

CMD ["sh", "-lc", "npm run migrate:deploy && node dist/index.js"]
