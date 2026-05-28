# Kaldi One — AWS Serverless Edition

Production-grade rebuild of [ai-qa-assistant](https://github.com/parshwa1956/ai-qa-assistant) using Vue 3, API Gateway HTTP API, Lambda (Python 3.12), DynamoDB, Cognito, S3, and CloudFront.

The original Streamlit app in the repo root is **unchanged**.

## Architecture summary

| Layer | Technology |
|-------|------------|
| Frontend | Vue 3 + Vite + TypeScript + Tailwind → private S3 + CloudFront OAC |
| API | API Gateway HTTP API + Cognito JWT authorizer |
| Compute | ARM64 Lambda (auth, projects, generation, history, files, jira, dashboard) |
| Data | DynamoDB single-table (on-demand) |
| Files | Private S3 uploads bucket (presigned URLs) |
| Secrets | Secrets Manager or SSM for OpenAI key; Jira token in DynamoDB (server-side only) |

See [architecture.md](./architecture.md) and [docs migration notes](#migration-from-streamlit--supabase) below.

## Prerequisites

- AWS CLI v2 configured with deploy permissions
- Node.js 20+ and npm
- Python 3.12+
- ACM certificate in **us-east-1** for your CloudFront domain
- Route53 hosted zone for `DomainName`
- OpenAI API key stored in Secrets Manager or SSM

## Quick deploy

```bash
cd aws-serverless-kaldi-one
cp infra/parameters.example.json infra/parameters.json
# Edit parameters.json (domain, hosted zone, certificate, secrets, origins)

./scripts/deploy-all.sh
```

`deploy-all.sh` will:

1. Package Lambda (`backend/build/lambda.zip`)
2. Upload artifact to `s3://{AppName}-{Environment}-deploy-{AccountId}/`
3. Deploy/update CloudFormation stack
4. Update all Lambda functions with the new zip
5. Build Vue app with stack outputs → `frontend/.env.production`
6. Sync `frontend/dist/` to the website bucket
7. Invalidate CloudFront

## Parameters (`infra/parameters.json`)

| Parameter | Description |
|-----------|-------------|
| `AppName` | Resource prefix (e.g. `kaldi-one`) |
| `Environment` | e.g. `prod` |
| `DomainName` | `app.example.com` |
| `HostedZoneId` | Route53 zone ID |
| `CertificateArn` | ACM ARN in us-east-1 |
| `OpenAISecretArn` | Secrets Manager ARN (preferred) |
| `OpenAIParameterName` | SSM path if not using Secrets Manager |
| `AllowedOrigins` | CORS origin(s), e.g. `https://app.example.com` |
| `PriceClass` | CloudFront price class |
| `LogRetentionDays` | CloudWatch retention |

## Local development

### Backend tests

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src pytest tests/ -q
```

### Frontend

```bash
cd frontend
cp .env.example .env.local
# Set VITE_* to your deployed stack outputs (or local mock API)
npm install
npm run dev
```

### Local API (optional)

Use [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) or invoke Lambdas directly with test events. For full integration, deploy a `dev` stack and point `.env.local` at it.

## Example API requests

Replace `$API`, `$TOKEN`, and IDs.

```bash
# Bootstrap user + General project
curl -s -X POST "$API/auth/bootstrap" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -d '{}'

# List projects
curl -s "$API/projects" -H "Authorization: Bearer $TOKEN"

# Generate test cases
curl -s -X POST "$API/generate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace": "qa",
    "outputType": "Test Cases",
    "title": "Login feature",
    "context": "User must log in with email and password.",
    "projectId": "YOUR_PROJECT_ID"
  }'

# Presigned upload
curl -s -X POST "$API/files/presign" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"filename":"screen.png","contentType":"image/png","projectId":"YOUR_PROJECT_ID"}'

# Save history
curl -s -X POST "$API/history" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"projectId":"...","itemType":"Test Cases","title":"Login tests","outputText":"..."}'

# Dashboard stats
curl -s "$API/dashboard" -H "Authorization: Bearer $TOKEN"
```

## Destroy

```bash
STACK_NAME=kaldi-one-prod ./infra/destroy.sh
```

Empty S3 buckets when prompted.

## Migration from Streamlit / Supabase

| Before | After |
|--------|-------|
| Supabase Auth | Amazon Cognito (email/password) |
| `profiles`, `projects`, `saved_items`, `jira_integrations` | DynamoDB single-table `USER#{id}` / `SK` patterns |
| Supabase Storage `screenshots` | S3 `{userId}/{projectId}/...` with presigned URLs |
| Streamlit session state | Vue Pinia + JWT + API persistence |
| Inline OpenAI in Streamlit | Generation Lambda + Secrets Manager |
| Jira token in DB (plaintext) | Token in DynamoDB; never returned to SPA after save |

Export Supabase data and map to DynamoDB items (see `architecture.md`).

## Project layout

```
aws-serverless-kaldi-one/
├── README.md
├── architecture.md
├── infra/
├── backend/
├── frontend/
└── scripts/
```

## Security notes

- S3 buckets block public access; website served only via CloudFront OAC
- CORS limited to `AllowedOrigins`
- All data APIs require Cognito JWT
- S3 keys scoped by Cognito `sub`
- HTTPS enforced on CloudFront with security response headers

## Cost optimization

- DynamoDB on-demand, Lambda ARM64, HTTP API (not REST), no NAT/RDS
- CloudFront `PriceClass_100` default
- Uploads lifecycle for `exports/` prefix (7 days)
- Configurable log retention
