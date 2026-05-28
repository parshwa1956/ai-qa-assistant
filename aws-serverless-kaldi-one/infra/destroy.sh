#!/usr/bin/env bash
set -euo pipefail

STACK_NAME="${STACK_NAME:-kaldi-one-prod}"
REGION="${AWS_REGION:-us-east-1}"

read -r -p "Delete stack ${STACK_NAME} in ${REGION}? Empty S3 buckets first. [y/N] " confirm
if [[ "${confirm}" != "y" && "${confirm}" != "Y" ]]; then
  echo "Aborted."
  exit 0
fi

echo "Emptying website and uploads buckets (if they exist)..."
for bucket in $(aws cloudformation describe-stack-resources \
  --stack-name "${STACK_NAME}" \
  --region "${REGION}" \
  --query "StackResources[?ResourceType=='AWS::S3::Bucket'].PhysicalResourceId" \
  --output text 2>/dev/null || true); do
  if [[ -n "${bucket}" && "${bucket}" != "None" ]]; then
    echo "  -> ${bucket}"
    aws s3 rm "s3://${bucket}" --recursive --region "${REGION}" 2>/dev/null || true
  fi
done

aws cloudformation delete-stack --stack-name "${STACK_NAME}" --region "${REGION}"
echo "Waiting for stack deletion..."
aws cloudformation wait stack-delete-complete --stack-name "${STACK_NAME}" --region "${REGION}"
echo "Stack deleted."
