#!/bin/bash
set -euo pipefail

REMOTE="rpi"
APP_DIR="/opt/coffee"

echo "=== Deploying Coffee Tracker to RPI (Docker) ==="

# Sync files
echo "[1/3] Syncing files..."
rsync -avz --delete \
  --rsync-path="sudo -n rsync" \
  --exclude '.git/' \
  --exclude '.DS_Store' \
  --exclude '.gitignore' \
  --exclude '.venv/' \
  --exclude '.cache/' \
  --exclude 'node_modules/' \
  --exclude 'data/' \
  --exclude 'logs/' \
  --exclude 'test/' \
  --exclude '.env' \
  ./ ${REMOTE}:${APP_DIR}/

# Ensure runtime dirs exist and make the dir writable by the SSH user
echo "[2/3] Ensuring data/logs directories exist..."
ssh ${REMOTE} "
  set -euo pipefail
  sudo -n mkdir -p ${APP_DIR}/data ${APP_DIR}/logs
  sudo -n chown -R \$(id -un):\$(id -gn) ${APP_DIR}
"

# Build + run
echo "[3/3] Building + starting containers..."
ssh ${REMOTE} "
  set -euo pipefail
  cd ${APP_DIR}

  DOCKER=\"docker\"
  if sudo -n docker version >/dev/null 2>&1; then
    DOCKER=\"sudo -n docker\"
  fi

  \${DOCKER} compose -f docker-compose.yml up -d --build --remove-orphans
  \${DOCKER} compose -f docker-compose.yml ps
"

echo ""
echo "=== Recent Logs ==="
ssh ${REMOTE} "
  set -euo pipefail
  cd ${APP_DIR}
  DOCKER=\"docker\"
  if sudo -n docker version >/dev/null 2>&1; then
    DOCKER=\"sudo -n docker\"
  fi
  \${DOCKER} compose -f docker-compose.yml logs -n 50
"
