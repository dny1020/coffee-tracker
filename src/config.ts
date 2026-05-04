import { z } from 'zod';

const envSchema = z
  .object({
    DATABASE_URL: z.string().min(1).default('file:/opt/coffee/data/coffee.db'),
    API_KEY: z.string().min(1).default('test-key'),
    LOG_LEVEL: z
      .enum(['fatal', 'error', 'warn', 'info', 'debug', 'trace', 'silent'])
      .default('info'),
    PORT: z.coerce.number().int().positive().default(8000),
    MAX_CAFFEINE_MG: z.coerce.number().int().positive().default(1000)
  })
  .passthrough();

export type AppConfig = z.infer<typeof envSchema>;

export function loadConfig(env: Record<string, unknown> = process.env): AppConfig {
  const parsed = envSchema.safeParse(env);
  if (!parsed.success) {
    const msg = parsed.error.issues.map((i) => `${i.path.join('.')}: ${i.message}`).join('; ');
    throw new Error(`Invalid environment: ${msg}`);
  }
  return parsed.data;
}
