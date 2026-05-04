#!/bin/bash
set -euo pipefail

REMOTE="rasperry"
APP_DIR="/opt/coffee"

echo "=== Deploying Coffee Tracker to RPI ==="

# Sync files
echo "[1/4] Syncing files..."
rsync -avz --delete \
  --rsync-path="sudo rsync" \
  --exclude '.git/' \
  --exclude '.DS_Store' \
  --exclude '.gitignore' \
  --exclude 'node_modules/' \
  --exclude 'dist/' \
  --exclude 'data/' \
  --exclude 'logs/' \
  --exclude 'test/' \
  --exclude '.env' \
  ./ ${REMOTE}:${APP_DIR}/

# Fix permissions
echo "[2/4] Setting permissions..."
ssh ${REMOTE} "sudo chown -R coffee:coffee ${APP_DIR} && sudo chmod 750 ${APP_DIR}"

# Install deps, build, and migrate
echo "[3/4] Installing dependencies + building..."
ssh ${REMOTE} "
  set -euo pipefail
  cd ${APP_DIR}

  # Ensure required runtime dirs exist
  sudo -u coffee mkdir -p data logs

  # Build requires devDependencies (typescript, prisma CLI)
  sudo -u coffee npm ci --include=dev --no-audit --no-fund
  sudo -u coffee npm run build

  # Apply DB migrations using DATABASE_URL from .env
  sudo -u coffee bash -lc 'cd ${APP_DIR} && set -a && source .env && set +a && npm run migrate:deploy'

  # Optional: remove devDependencies after build/migrate to keep the install lean
  sudo -u coffee npm prune --omit=dev
"

# Install service if not present
ssh ${REMOTE} "
  if [ ! -f /etc/systemd/system/coffee.service ]; then
    echo 'Installing systemd service...'
    sudo cp ${APP_DIR}/coffee.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable coffee
  fi
"

# Restart
echo "[4/4] Restarting service..."
ssh ${REMOTE} "sudo systemctl restart coffee"

sleep 3
echo "=== Service Status ==="
ssh ${REMOTE} "sudo systemctl status coffee --no-pager -l"

echo ""
echo "=== Recent Logs ==="
ssh ${REMOTE} "journalctl -u coffee.service -n 20 --no-pager"
