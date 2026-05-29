# IAM permissions for `deploy-all.sh`

## Why deploy failed

User **`temp`** currently has only **`AmazonS3FullAccess`**.  
`./scripts/deploy-all.sh` also needs **CloudFormation**, **IAM** (named roles), **Lambda**, **API Gateway**, **Cognito**, **DynamoDB**, **CloudFront**, **Route53**, and **CloudWatch Logs**.

Error you saw:

```text
cloudformation:DescribeStacks ... AccessDenied
```

## Fix (account admin required)

An **admin** (or root) must attach deploy permissions to `temp`.

### Option 1 — Custom policy (recommended)

1. IAM → **Policies** → **Create policy** → **JSON**
2. Paste contents of [`iam-kaldi-one-deploy-policy.json`](./iam-kaldi-one-deploy-policy.json)
3. Replace `085165114087` and `us-east-1` if your account/region differ
4. Name: `KaldiOneDeployPolicy`
5. IAM → **Users** → **temp** → **Add permissions** → **Attach policies** → select `KaldiOneDeployPolicy`

Keep or remove `AmazonS3FullAccess` (the custom policy already includes S3 for `kaldi-one-*` buckets).

### Option 2 — AWS managed (broader, faster for testing)

Attach these managed policies to `temp` (more access than needed):

- `AWSCloudFormationFullAccess`
- `IAMFullAccess` (required for `CAPABILITY_NAMED_IAM`)
- `AWSLambda_FullAccess`
- `AmazonAPIGatewayAdministrator`
- `AmazonCognitoPowerUser`
- `AmazonDynamoDBFullAccess`
- `CloudFrontFullAccess`
- `AmazonRoute53FullAccess`
- `CloudWatchLogsFullAccess`
- `AmazonS3FullAccess` (already attached)

### Option 3 — Use an admin profile locally

```bash
export AWS_PROFILE=your-admin-profile
./scripts/deploy-all.sh
```

## Verify credentials

```bash
aws sts get-caller-identity
aws cloudformation describe-stacks --stack-name kaldi-one-prod --region us-east-1
```

Second command should succeed (or return “stack does not exist” on first deploy — not AccessDenied).

## Pip warning during packaging

If you see `aiobotocore` / `botocore` conflict: that is your **local** Python environment.  
`package-backend.sh` now uses an isolated venv so Lambda packaging is unaffected. The zip was still created successfully before the CloudFormation step failed.
