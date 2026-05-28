# Migration: Streamlit + Supabase → AWS Serverless Kaldi One

## Feature parity checklist

| Feature | Streamlit | AWS edition |
|---------|-----------|-------------|
| Sign up / login / forgot password | Supabase Auth | Cognito |
| Projects + General default | `projects` table | DynamoDB + bootstrap |
| QA / BA / Dev / Flow workspaces | Tabs in `1_Login_and_Start.py` | Vue Workspace view |
| OpenAI generators | Inline prompts | `services/openai_service.py` |
| Smart Code Review | Mock / real flag | `ENABLE_REAL_CODE_REVIEW` env |
| History search/filter | `10_History.py` | `GET /history?q=` |
| Exports TXT/CSV/XLSX | `openpyxl` in Streamlit | `POST /history/{id}/export` |
| Jira save/test/create | Settings + inline | `jira` Lambda |
| Dashboard | `2_Dashboard.py` | `GET /dashboard` |
| Screenshot storage | Supabase bucket | S3 presigned |

## Data migration steps

### 1. Export Supabase

Export CSV/JSON for:

- `profiles` → `PK=USER#{id}`, `SK=PROFILE`
- `projects` → `SK=PROJECT#{id}`, set `isDefault=true` for name `General`
- `saved_items` → `SK=ITEM#{created_at}#{id}`, populate GSI1PK/GSI1SK
- `jira_integrations` → `SK=JIRA` (consider re-encrypting token with KMS)

### 2. Map columns

**saved_items → DynamoDB ITEM**

```
user_id → PK prefix
id → itemId
project_id → projectId + GSI1PK
item_type → itemType
title, input_context, output_text → camelCase fields
screenshot_path → screenshotPath (copy objects to S3 with same key layout)
```

### 3. Storage migration

```bash
# Example: sync from Supabase export to uploads bucket
aws s3 sync ./supabase-screenshots-export s3://YOUR_UPLOADS_BUCKET/
```

Ensure object keys remain `{userId}/{projectId}/...` for authorization.

### 4. Users

- Recreate users in Cognito (no password hash migration from Supabase)
- Send password reset emails or communicate temporary passwords
- On first login, bootstrap creates General project if missing

## Prompt / output compatibility

JSON schemas are preserved from the monolithic Streamlit file. Downstream Jira ADF builder and DataFrame exports use the same field names (`Test Case ID`, `User Story ID`, etc.).

## Environment mapping

| Streamlit / Supabase | AWS |
|---------------------|-----|
| `OPENAI_API_KEY` | Secrets Manager / SSM |
| `SUPABASE_URL` / `SUPABASE_KEY` | Removed |
| `PASSWORD_RESET_REDIRECT` | Cognito app client callback/logout URLs |
| Cookie `sb_access_token` | Cognito ID token in SPA |

## Operational differences

- **Cold starts**: First generation after idle may add latency; increase memory if needed.
- **Timeout**: Generation Lambda 120s vs long Streamlit sessions.
- **PDF flows**: Full `gpt-4.1` PDF path from Streamlit can be added to generation service (image/text supported in v1).
- **Pro/Stripe**: Marketing only in original app; not enforced in AWS edition.

## Rollback

Keep Streamlit deployment running until AWS path is validated. The repo root Streamlit code is untouched.
