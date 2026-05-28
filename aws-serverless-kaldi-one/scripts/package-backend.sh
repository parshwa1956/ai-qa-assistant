#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="${ROOT_DIR}/backend"
BUILD_DIR="${BACKEND_DIR}/build"
PKG_DIR="${BUILD_DIR}/package"
OUT_ZIP="${BUILD_DIR}/lambda.zip"

rm -rf "${BUILD_DIR}"
mkdir -p "${PKG_DIR}"

pip install -r "${BACKEND_DIR}/requirements.txt" -t "${PKG_DIR}" --upgrade --quiet

cp -R "${BACKEND_DIR}/src/"* "${PKG_DIR}/"

cd "${PKG_DIR}"
zip -qr "${OUT_ZIP}" . -x "*.pyc" -x "__pycache__/*"
echo "Created ${OUT_ZIP} ($(du -h "${OUT_ZIP}" | cut -f1))"
