import type { FastifyPluginAsync } from 'fastify';
import type { PrismaClient } from '@prisma/client';
import { DateTime } from 'luxon';

import type { AppConfig } from '../config';
import { verifyApiKey } from '../auth';

const BOGOTA_TZ = 'America/Bogota';

type CoffeeRoutesOpts = {
  prisma: PrismaClient;
  config: AppConfig;
};

const coffeeRoutes: FastifyPluginAsync<CoffeeRoutesOpts> = async (app, opts) => {
  app.addHook('preHandler', verifyApiKey(opts.config));

  app.post(
    '/',
    {
      schema: {
        body: {
          type: 'object',
          required: ['caffeine_mg'],
          additionalProperties: false,
          properties: {
            caffeine_mg: { type: 'number', minimum: 0, maximum: opts.config.MAX_CAFFEINE_MG },
            coffee_type: { anyOf: [{ type: 'string', maxLength: 100 }, { type: 'null' }] }
          }
        },
        response: {
          200: {
            type: 'object',
            required: ['id', 'timestamp', 'caffeine_mg', 'coffee_type'],
            properties: {
              id: { type: 'integer' },
              timestamp: { type: 'string', format: 'date-time' },
              caffeine_mg: { type: 'number' },
              coffee_type: { anyOf: [{ type: 'string' }, { type: 'null' }] }
            }
          }
        },
        tags: ['coffee'],
        security: [{ bearerAuth: [] }]
      }
    },
    async (request) => {
      const body = request.body as { caffeine_mg: number; coffee_type?: string | null };
      const coffee = await opts.prisma.coffeeLog.create({
        data: {
          caffeine_mg: body.caffeine_mg,
          coffee_type: body.coffee_type ?? null
        }
      });
      return coffee;
    }
  );

  app.get(
    '/',
    {
      schema: {
        querystring: {
          type: 'object',
          additionalProperties: false,
          properties: {
            limit: { type: 'integer', minimum: 1, maximum: 500, default: 50 }
          }
        },
        response: {
          200: {
            type: 'array',
            items: {
              type: 'object',
              required: ['id', 'timestamp', 'caffeine_mg', 'coffee_type'],
              properties: {
                id: { type: 'integer' },
                timestamp: { type: 'string', format: 'date-time' },
                caffeine_mg: { type: 'number' },
                coffee_type: { anyOf: [{ type: 'string' }, { type: 'null' }] }
              }
            }
          }
        },
        tags: ['coffee'],
        security: [{ bearerAuth: [] }]
      }
    },
    async (request) => {
      const qs = (request.query ?? {}) as { limit?: number };
      const limit = typeof qs.limit === 'number' ? qs.limit : 50;
      return opts.prisma.coffeeLog.findMany({
        orderBy: { timestamp: 'desc' },
        take: limit
      });
    }
  );

  app.delete(
    '/:id',
    {
      schema: {
        params: {
          type: 'object',
          required: ['id'],
          additionalProperties: false,
          properties: {
            id: { type: 'integer' }
          }
        },
        response: {
          200: {
            type: 'object',
            required: ['deleted'],
            properties: { deleted: { type: 'integer' } }
          },
          404: {
            type: 'object',
            required: ['detail'],
            properties: { detail: { type: 'string' } }
          }
        },
        tags: ['coffee'],
        security: [{ bearerAuth: [] }]
      }
    },
    async (request, reply) => {
      const params = request.params as { id: number };
      const existing = await opts.prisma.coffeeLog.findUnique({ where: { id: params.id } });
      if (!existing) {
        return reply.status(404).send({ detail: 'Not found' });
      }
      await opts.prisma.coffeeLog.delete({ where: { id: params.id } });
      return { deleted: params.id };
    }
  );

  app.get(
    '/today',
    {
      schema: {
        response: {
          200: {
            type: 'object',
            required: ['total_caffeine_mg', 'coffee_types', 'peak_hour', 'coffees'],
            properties: {
              total_caffeine_mg: { type: 'number' },
              coffee_types: { type: 'array', items: { type: 'string' } },
              peak_hour: { anyOf: [{ type: 'integer' }, { type: 'null' }] },
              coffees: {
                type: 'array',
                items: {
                  type: 'object',
                  required: ['time', 'type', 'caffeine_mg'],
                  properties: {
                    time: { type: 'string' },
                    type: { anyOf: [{ type: 'string' }, { type: 'null' }] },
                    caffeine_mg: { type: 'number' }
                  }
                }
              }
            }
          }
        },
        tags: ['coffee'],
        security: [{ bearerAuth: [] }]
      }
    },
    async () => {
      const nowLocal = DateTime.now().setZone(BOGOTA_TZ);
      const startUtc = nowLocal.startOf('day').toUTC().toJSDate();

      const logs = await opts.prisma.coffeeLog.findMany({
        where: { timestamp: { gte: startUtc } }
      });

      const total = logs.reduce((sum, l) => sum + l.caffeine_mg, 0);
      const totalRounded = Math.round(total * 10) / 10;

      const types = new Set<string>();
      for (const l of logs) {
        if (l.coffee_type) types.add(l.coffee_type);
      }

      const hourCounts = new Map<number, number>();
      for (const l of logs) {
        const hour = DateTime.fromJSDate(l.timestamp, { zone: 'utc' }).setZone(BOGOTA_TZ).hour;
        hourCounts.set(hour, (hourCounts.get(hour) ?? 0) + 1);
      }

      let peak_hour: number | null = null;
      let peakCount = 0;
      for (const [hour, count] of hourCounts.entries()) {
        if (count > peakCount) {
          peakCount = count;
          peak_hour = hour;
        }
      }

      return {
        total_caffeine_mg: totalRounded,
        coffee_types: Array.from(types),
        peak_hour,
        coffees: logs.map((l) => ({
          time: DateTime.fromJSDate(l.timestamp, { zone: 'utc' }).setZone(BOGOTA_TZ).toFormat('HH:mm'),
          type: l.coffee_type ?? null,
          caffeine_mg: l.caffeine_mg
        }))
      };
    }
  );

  app.get(
    '/stats',
    {
      schema: {
        querystring: {
          type: 'object',
          additionalProperties: false,
          properties: {
            days: { type: 'integer', minimum: 1, maximum: 365, default: 30 }
          }
        },
        response: {
          200: {
            type: 'object',
            required: ['total_caffeine_mg', 'coffee_types', 'peak_hours'],
            properties: {
              total_caffeine_mg: { type: 'number' },
              coffee_types: {
                type: 'array',
                items: {
                  type: 'object',
                  required: ['type', 'count'],
                  properties: {
                    type: { type: 'string' },
                    count: { type: 'integer' }
                  }
                }
              },
              peak_hours: {
                type: 'array',
                items: {
                  type: 'object',
                  required: ['hour', 'count'],
                  properties: {
                    hour: { type: 'integer' },
                    count: { type: 'integer' }
                  }
                }
              }
            }
          }
        },
        tags: ['coffee'],
        security: [{ bearerAuth: [] }]
      }
    },
    async (request) => {
      const qs = (request.query ?? {}) as { days?: number };
      const days = typeof qs.days === 'number' ? qs.days : 30;

      const cutoffUtc = DateTime.now().setZone(BOGOTA_TZ).minus({ days }).toUTC().toJSDate();
      const logs = await opts.prisma.coffeeLog.findMany({
        where: { timestamp: { gte: cutoffUtc } }
      });

      if (logs.length === 0) {
        return { total_caffeine_mg: 0, coffee_types: [], peak_hours: [] };
      }

      const total = logs.reduce((sum, l) => sum + l.caffeine_mg, 0);
      const totalRounded = Math.round(total * 10) / 10;

      const typeCounts = new Map<string, number>();
      const hourCounts = new Map<number, number>();

      for (const l of logs) {
        if (l.coffee_type) typeCounts.set(l.coffee_type, (typeCounts.get(l.coffee_type) ?? 0) + 1);

        const hour = DateTime.fromJSDate(l.timestamp, { zone: 'utc' }).setZone(BOGOTA_TZ).hour;
        hourCounts.set(hour, (hourCounts.get(hour) ?? 0) + 1);
      }

      const coffee_types = Array.from(typeCounts.entries())
        .sort((a, b) => b[1] - a[1])
        .map(([type, count]) => ({ type, count }));

      const peak_hours = Array.from(hourCounts.entries())
        .sort((a, b) => b[1] - a[1])
        .slice(0, 3)
        .map(([hour, count]) => ({ hour, count }));

      return {
        total_caffeine_mg: totalRounded,
        coffee_types,
        peak_hours
      };
    }
  );
};

export default coffeeRoutes;
