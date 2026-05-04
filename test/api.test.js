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
