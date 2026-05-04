import { buildApp } from './app';
import { loadConfig } from './config';

async function main() {
  const config = loadConfig();
  const app = await buildApp(config);

  try {
    await app.listen({
      host: '0.0.0.0',
      port: config.PORT
    });
  } catch (err) {
    app.log.error(err);
    process.exit(1);
  }
}

main();
