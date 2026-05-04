function verifyApiKey(config) {
  return async function (request, reply) {
    const auth = request.headers.authorization;
    const token = auth?.toLowerCase().startsWith('bearer ') ? auth.slice(7) : undefined;

    if (!token || token !== config.API_KEY) {
      return reply.status(401).send({ detail: 'Invalid API key' });
    }
  };
}

module.exports = { verifyApiKey };
