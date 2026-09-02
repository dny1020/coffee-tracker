const test = require('node:test');
const assert = require('node:assert/strict');

const { buildApp } = require('../src/app');
const { loadConfig } = require('../src/config');

function makeEnv(overrides = {}) {
  return {
    ...process.env,
    DATABASE_URL: 'file:./data/test.db',
    API_KEY: 'test-key',
    LOG_LEVEL: 'silent',
    PORT: '8000',
    ...overrides
  };
}

test('GET /api/v1/health', async () => {
  const app = await buildApp(loadConfig(makeEnv()));
  await app.ready();

  const res = await app.inject({ method: 'GET', url: '/api/v1/health' });
  assert.equal(res.statusCode, 200);
  assert.deepEqual(res.json(), { status: 'ok' });

  await app.close();
});

test('GET /api/v1/docs', async () => {
  const app = await buildApp(loadConfig(makeEnv()));
  await app.ready();

  const res = await app.inject({ method: 'GET', url: '/api/v1/docs' });
  assert.equal(res.statusCode, 200);

  await app.close();
});

test('coffee endpoints require Bearer API key', async () => {
  const app = await buildApp(loadConfig(makeEnv()));
  await app.ready();

  const res = await app.inject({ method: 'GET', url: '/api/v1/coffee/' });
  assert.equal(res.statusCode, 401);
  assert.deepEqual(res.json(), { detail: 'Invalid API key' });

  await app.close();
});

test('GET /api/v1/coffee/stats is public', async () => {
  const app = await buildApp(loadConfig(makeEnv()));
  await app.ready();

  const res = await app.inject({ method: 'GET', url: '/api/v1/coffee/stats' });
  assert.equal(res.statusCode, 200);
  assert.ok('total_caffeine_mg' in res.json());

  await app.close();
});

test('the public stats route does not open the write path', async () => {
  const app = await buildApp(loadConfig(makeEnv()));
  await app.ready();

  // A valid payload on the POST, so the 401 comes from the auth hook rather
  // than from schema validation, which Fastify runs first.
  for (const [method, url, payload] of [
    ['POST', '/api/v1/coffee', { caffeine_mg: 80, coffee_type: 'espresso' }],
    ['GET', '/api/v1/coffee', undefined],
    ['GET', '/api/v1/coffee/today', undefined],
    ['DELETE', '/api/v1/coffee/1', undefined]
  ]) {
    const res = await app.inject({ method, url, payload });
    assert.equal(res.statusCode, 401, `${method} ${url} should require the key`);
  }

  await app.close();
});

test('API_KEY has no default', () => {
  const env = makeEnv();
  delete env.API_KEY;
  assert.throws(() => loadConfig(env), /API_KEY/);
});

test('CORS answers the configured origin and refuses others', async () => {
  const app = await buildApp(loadConfig(makeEnv({ CORS_ORIGINS: 'https://danilocloud.me' })));
  await app.ready();

  const allowed = await app.inject({
    method: 'GET',
    url: '/api/v1/coffee/stats',
    headers: { origin: 'https://danilocloud.me' }
  });
  assert.equal(allowed.headers['access-control-allow-origin'], 'https://danilocloud.me');

  const other = await app.inject({
    method: 'GET',
    url: '/api/v1/coffee/stats',
    headers: { origin: 'https://example.com' }
  });
  assert.equal(other.headers['access-control-allow-origin'], undefined);

  await app.close();
});
