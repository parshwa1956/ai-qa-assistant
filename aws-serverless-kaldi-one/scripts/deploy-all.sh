#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INFRA_DIR="${ROOT_DIR}/infra"
PARAMS_FILE="${PARAMS_FILE:-${INFRA_DIR}/parameters.json}"
STACK_NAME="${STACK_NAME:-kaldi-one-prod}"
REGION="${AWS_REGION:-us-east-1}"
ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"

if [[ ! -f "${PARAMS_FILE}" ]]; then
  echo "Copy infra/parameters.example.json to infra/parameters.json and configure values."
  exit 1
fi

echo "==> Checking AWS credentials"
CALLER="$(aws sts get-caller-identity --query Arn --output text 2>&1)" || {
  echo "ERROR: AWS CLI not configured. Run: aws configure"
  exit 1
}
echo "    Caller: ${CALLER}"

if ! aws cloudformation describe-stacks --stack-name "${STACK_NAME}" --region "${REGION}" >/dev/null 2>&1; then
  CF_ERR="$(aws cloudformation describe-stacks --stack-name "${STACK_NAME}" --region "${REGION}" 2>&1 || true)"
  if echo "${CF_ERR}" | grep -q AccessDenied; then
    echo ""
    echo "ERROR: This IAM user cannot call CloudFormation."
    echo "       Attach deploy policy from infra/IAM-DEPLOY.md (user temp only has S3 today)."
    echo ""
    exit 1
  fi
  # Stack may not exist yet on first deploy — that is OK
  echo "    CloudFormation access OK (stack may not exist yet)"
fi

APP_NAME="$(python3 -c "import json; print([p['ParameterValue'] for p in json.load(open('${PARAMS_FILE}')) if p['ParameterKey']=='AppName'][0])")"
ENV_NAME="$(python3 -c "import json; print([p['ParameterValue'] for p in json.load(open('${PARAMS_FILE}')) if p['ParameterKey']=='Environment'][0])")"
ARTIFACT_BUCKET="${APP_NAME}-${ENV_NAME}-deploy-${ACCOUNT_ID}"

echo "==> Packaging backend"
bash "${ROOT_DIR}/scripts/package-backend.sh"

echo "==> Ensuring artifact bucket s3://${ARTIFACT_BUCKET}"
if ! aws s3api head-bucket --bucket "${ARTIFACT_BUCKET}" 2>/dev/null; then
  aws s3api create-bucket --bucket "${ARTIFACT_BUCKET}" --region "${REGION}" 2>/dev/null || \
  aws s3api create-bucket --bucket "${ARTIFACT_BUCKET}" --region "${REGION}" --create-bucket-configuration LocationConstraint="${REGION}"
  aws s3api put-public-access-block --bucket "${ARTIFACT_BUCKET}" --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
fi

aws s3 cp "${ROOT_DIR}/backend/build/lambda.zip" "s3://${ARTIFACT_BUCKET}/backend/lambda.zip"

TMP_PARAMS="$(mktemp)"
python3 <<PY
import json
params = json.load(open("${PARAMS_FILE}"))
extra = [
  {"ParameterKey": "LambdaArtifactBucket", "ParameterValue": "${ARTIFACT_BUCKET}"},
  {"ParameterKey": "LambdaArtifactKey", "ParameterValue": "backend/lambda.zip"},
]
keys = {p["ParameterKey"] for p in params}
for e in extra:
    if e["ParameterKey"] not in keys:
        params.append(e)
    else:
        for p in params:
            if p["ParameterKey"] == e["ParameterKey"]:
                p["ParameterValue"] = e["ParameterValue"]
json.dump(params, open("${TMP_PARAMS}", "w"), indent=2)
PY

echo "==> Deploying CloudFormation stack ${STACK_NAME}"
aws cloudformation deploy \
  --template-file "${INFRA_DIR}/cloudformation.yaml" \
  --stack-name "${STACK_NAME}" \
  --parameter-overrides file://"${TMP_PARAMS}" \
  --capabilities CAPABILITY_NAMED_IAM \
  --region "${REGION}" \
  --no-fail-on-empty-changeset

rm -f "${TMP_PARAMS}"

get_output() {
  aws cloudformation describe-stacks --stack-name "${STACK_NAME}" --region "${REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='$1'].OutputValue" --output text
}

API_URL="$(get_output ApiEndpoint)"
POOL_ID="$(get_output CognitoUserPoolId)"
CLIENT_ID="$(get_output CognitoUserPoolClientId)"
WEB_BUCKET="$(get_output WebsiteBucketName)"
CUSTOM_URL="$(get_output CustomDomainURL)"
ISSUER="$(get_output CognitoIssuer)"

cat > "${ROOT_DIR}/.deploy.env" <<EOF
export VITE_API_BASE_URL=${API_URL}
export VITE_COGNITO_USER_POOL_ID=${POOL_ID}
export VITE_COGNITO_CLIENT_ID=${CLIENT_ID}
export VITE_COGNITO_REGION=${REGION}
export VITE_APP_URL=${CUSTOM_URL}
EOF

cat > "${ROOT_DIR}/frontend/.env.production" <<EOF
VITE_API_BASE_URL=${API_URL}
VITE_COGNITO_USER_POOL_ID=${POOL_ID}
VITE_COGNITO_CLIENT_ID=${CLIENT_ID}
VITE_COGNITO_REGION=${REGION}
VITE_APP_NAME=Kaldi One
VITE_APP_URL=${CUSTOM_URL}
EOF

echo "==> Updating Lambda code on all functions"
for fn in $(aws lambda list-functions --region "${REGION}" --query "Functions[?starts_with(FunctionName, '${APP_NAME}-${ENV_NAME}')].FunctionName" --output text); do
  aws lambda update-function-code \
    --function-name "${fn}" \
    --s3-bucket "${ARTIFACT_BUCKET}" \
    --s3-key backend/lambda.zip \
    --region "${REGION}" >/dev/null
  echo "  updated ${fn}"
done

echo "==> Building and syncing frontend"
# shellcheck disable=SC1091
source "${ROOT_DIR}/.deploy.env"
bash "${ROOT_DIR}/scripts/build-frontend.sh"
aws s3 sync "${ROOT_DIR}/frontend/dist/" "s3://${WEB_BUCKET}/" --delete --region "${REGION}"

CF_ID="$(aws cloudformation describe-stack-resources --stack-name "${STACK_NAME}" --region "${REGION}" \
  --logical-resource-id CloudFrontDistribution --query 'StackResources[0].PhysicalResourceId' --output text)"
aws cloudfront create-invalidation --distribution-id "${CF_ID}" --paths "/*" >/dev/null
echo "CloudFront invalidation submitted."

echo ""
echo "Deployment complete."
echo "  App URL: ${CUSTOM_URL}"
echo "  API:     ${API_URL}"
