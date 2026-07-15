#!/usr/bin/env bash
set -euo pipefail
if [ -z "${1:-}" ]; then
  echo "Usage: ./scripts/deploy.sh <environment>"
  exit 1
fi

echo "Deploying to $1"
docker compose up --build -d
