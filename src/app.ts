import Fastify from 'fastify';
import swagger from '@fastify/swagger';
import swaggerUi from '@fastify/swagger-ui';
import { PrismaClient } from '@prisma/client';
import { PrismaLibSql } from '@prisma/adapter-libsql';

import type { AppConfig } from './config';
import coffeeRoutes from './routes/coffee';

export async function buildApp(config: AppConfig) {
  const app = Fastify({
    routerOptions: {
      ignoreTrailingSlash: true
    },
    logger: {
      level: config.LOG_LEVEL,
      transport: {
        targets: [
          { target: 'pino/file', level: config.LOG_LEVEL, options: { destination: 1 } },
          { target: 'pino/file', level: config.LOG_LEVEL, options: { destination: 'logs/app.log', mkdir: true } }
        ]
      }
    }
  });

  const adapter = new PrismaLibSql({
    url: config.DATABASE_URL
  });
  const prisma = new PrismaClient({ adapter });

  app.addHook('onClose', async () => {
    await prisma.$disconnect();
  });

  await app.register(swagger, {
    openapi: {
      info: {
        title: 'Coffee Tracker',
        version: '1.0.0'
      },
      components: {
        securitySchemes: {
          bearerAuth: {
            type: 'http',
            scheme: 'bearer'
          }
        }
      }
    }
  });

  await app.register(swaggerUi, {
    routePrefix: '/api/v1/docs',
    uiConfig: {
      docExpansion: 'list',
      deepLinking: false
    }
  });

  app.get(
    '/api/v1/health',
    {
      schema: {
        response: {
          200: {
            type: 'object',
            required: ['status'],
            properties: { status: { type: 'string' } }
          }
        },
        tags: ['health']
      }
    },
    async () => ({ status: 'ok' })
  );

  await app.register(coffeeRoutes, {
    prefix: '/api/v1/coffee',
    prisma,
    config
  });

  return app;
}
