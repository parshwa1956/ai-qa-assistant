#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PARAMS_FILE="${1:-${SCRIPT_DIR}/parameters.json}"
STACK_NAME="${STACK_NAME:-kaldi-one-prod}"
REGION="${AWS_REGION:-us-east-1}"

if [[ ! -f "${PARAMS_FILE}" ]]; then
  echo "Parameters file not found: ${PARAMS_FILE}"
  echo "Copy parameters.example.json to parameters.json and fill in values."
  exit 1
fi

echo "Deploying CloudFormation stack: ${STACK_NAME} (${REGION})"
aws cloudformation deploy \
  --template-file "${SCRIPT_DIR}/cloudformation.yaml" \
  --stack-name "${STACK_NAME}" \
  --parameter-overrides file://"${PARAMS_FILE}" \
  --capabilities CAPABILITY_NAMED_IAM \
  --region "${REGION}" \
  --no-fail-on-empty-changeset

echo "Stack outputs:"
aws cloudformation describe-stacks \
  --stack-name "${STACK_NAME}" \
  --region "${REGION}" \
  --query 'Stacks[0].Outputs' \
  --output table

echo "Done. Run scripts/deploy-all.sh from repo root to publish frontend and Lambda code."
