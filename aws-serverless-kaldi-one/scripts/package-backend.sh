#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="${ROOT_DIR}/backend"
BUILD_DIR="${BACKEND_DIR}/build"
PKG_DIR="${BUILD_DIR}/package"
OUT_ZIP="${BUILD_DIR}/lambda.zip"
VENV_DIR="${BUILD_DIR}/.venv"

rm -rf "${BUILD_DIR}"
mkdir -p "${PKG_DIR}"

# Isolated venv avoids conflicts with system packages (e.g. aiobotocore vs botocore)
python3 -m venv "${VENV_DIR}"
"${VENV_DIR}/bin/pip" install --upgrade pip -q
"${VENV_DIR}/bin/pip" install -r "${BACKEND_DIR}/requirements.txt" -t "${PKG_DIR}" --upgrade -q

cp -R "${BACKEND_DIR}/src/"* "${PKG_DIR}/"

cd "${PKG_DIR}"
zip -qr "${OUT_ZIP}" . -x "*.pyc" -x "__pycache__/*"
echo "Created ${OUT_ZIP} ($(du -h "${OUT_ZIP}" | cut -f1))"
