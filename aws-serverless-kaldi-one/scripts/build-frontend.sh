#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="${ROOT_DIR}/frontend"
ENV_FILE="${FRONTEND_DIR}/.env.production"

if [[ -f "${ROOT_DIR}/.deploy.env" ]]; then
  # shellcheck disable=SC1091
  source "${ROOT_DIR}/.deploy.env"
fi

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing ${ENV_FILE}. Run deploy-all.sh first or copy .env.example."
  exit 1
fi

cd "${FRONTEND_DIR}"
if [[ ! -d node_modules ]]; then
  npm ci
fi
npm run build
echo "Frontend built to ${FRONTEND_DIR}/dist"
