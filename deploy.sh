#!/bin/bash
set -euo pipefail

REMOTE="rpi"
APP_DIR="coffee"  # deployed under remote user's home directory

echo "=== Deploying Coffee Tracker to RPI (Docker) ==="

# Ensure app dir exists
ssh ${REMOTE} "set -euo pipefail; mkdir -p ${APP_DIR}"

# Sync files
echo "[1/3] Syncing files..."
rsync -avz --delete \
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

# Ensure runtime dirs exist
echo "[2/3] Ensuring data/logs directories exist..."
ssh ${REMOTE} "set -euo pipefail; mkdir -p ${APP_DIR}/data ${APP_DIR}/logs"

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
