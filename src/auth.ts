import type { FastifyReply, FastifyRequest } from 'fastify';
import type { AppConfig } from './config';

export function verifyApiKey(config: Pick<AppConfig, 'API_KEY'>) {
  return async function (request: FastifyRequest, reply: FastifyReply) {
    const auth = request.headers.authorization;
    const token = auth?.toLowerCase().startsWith('bearer ') ? auth.slice(7) : undefined;

    if (!token || token !== config.API_KEY) {
      return reply.status(401).send({ detail: 'Invalid API key' });
    }
  };
}
