const { createHash, timingSafeEqual } = require('node:crypto');

// Hash both sides first: timingSafeEqual throws on a length mismatch, which
// would otherwise leak the key length.
function digest(value) {
  return createHash('sha256').update(value, 'utf8').digest();
}

function verifyApiKey(config) {
  const expected = digest(config.API_KEY);

  return async function (request, reply) {
    const auth = request.headers.authorization;
    const token = auth?.toLowerCase().startsWith('bearer ') ? auth.slice(7) : undefined;

    if (!token || !timingSafeEqual(digest(token), expected)) {
      return reply.status(401).send({ detail: 'Invalid API key' });
    }
  };
}

module.exports = { verifyApiKey };
