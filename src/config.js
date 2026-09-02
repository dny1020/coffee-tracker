const { z } = require('zod');

const envSchema = z
  .object({
    DATABASE_URL: z.string().min(1).default('file:./data/coffee.db'),
    // No default. A public deployment must not fall back to a guessable key.
    API_KEY: z.string().min(1),
    // Comma-separated origins allowed to call the public read endpoints.
    CORS_ORIGINS: z.string().default(''),
    LOG_LEVEL: z
      .enum(['fatal', 'error', 'warn', 'info', 'debug', 'trace', 'silent'])
      .default('info'),
    PORT: z.coerce.number().int().positive().default(8000),
    MAX_CAFFEINE_MG: z.coerce.number().int().positive().default(1000)
  })
  .passthrough();

function loadConfig(env = process.env) {
  const parsed = envSchema.safeParse(env);
  if (!parsed.success) {
    const msg = parsed.error.issues.map((i) => `${i.path.join('.')}: ${i.message}`).join('; ');
    throw new Error(`Invalid environment: ${msg}`);
  }
  return parsed.data;
}

module.exports = { loadConfig };
