#!/bin/bash
set -e

REMOTE="rasperry"
APP_DIR="/opt/coffee"

echo "=== Deploying Coffee Tracker to RPI ==="

# Sync files
echo "[1/4] Syncing files..."
rsync -avz --delete \
  --rsync-path="sudo rsync" \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude '.venv/' \
  --exclude '.git/' \
  --exclude '.DS_Store' \
  --exclude '.gitignore' \
  --exclude '.pytest_cache/' \
  --exclude 'data/' \
  --exclude 'logs/' \
  --exclude 'tests/' \
  ./ ${REMOTE}:${APP_DIR}/

# Fix permissions
echo "[2/4] Setting permissions..."
ssh ${REMOTE} "sudo chown -R coffee:coffee ${APP_DIR} && sudo chmod 750 ${APP_DIR}"

# Setup venv and deps if needed
echo "[3/4] Checking dependencies..."
ssh ${REMOTE} "
  if [ ! -d ${APP_DIR}/.venv ]; then
    echo 'Creating virtualenv...'
    sudo -u coffee python3 -m venv ${APP_DIR}/.venv
  fi
  sudo -u coffee ${APP_DIR}/.venv/bin/pip install -q -r ${APP_DIR}/requirements.txt
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
