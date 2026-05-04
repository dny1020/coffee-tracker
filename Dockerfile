FROM docker.io/library/node:20-bookworm-slim

WORKDIR /app
ENV NODE_ENV=production

RUN apt-get update -y \
  && apt-get install -y --no-install-recommends openssl \
  && rm -rf /var/lib/apt/lists/*

COPY package.json package-lock.json ./
COPY prisma ./prisma
COPY prisma.config.js ./
COPY src ./src

RUN npm ci --omit=dev --no-audit --no-fund
RUN ./node_modules/.bin/prisma generate

EXPOSE 8000

# Apply migrations (baseline if DB already exists), then start server
CMD ["sh", "-lc", "./node_modules/.bin/prisma migrate deploy || (./node_modules/.bin/prisma migrate resolve --applied 20260503214403_init && ./node_modules/.bin/prisma migrate deploy); node src/index.js"]
