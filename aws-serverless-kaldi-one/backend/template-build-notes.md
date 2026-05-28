# Lambda packaging notes

- Handler path in CloudFormation: `handlers.<module>.handler`
- Package root must be `backend/src` contents at zip root (so `handlers/` and `common/` are top-level).
- Dependencies install into package root: `pip install -r requirements.txt -t package/`
- Use **arm64** compatible wheels when building on Apple Silicon: `pip install --platform manylinux2014_aarch64 --only-binary=:all:` if cross-compiling.
- OpenAI SDK is only required in `generation` and `code_review_service`; still bundled in shared artifact for simplicity.
- Max deployment package: watch 50MB direct upload / 250MB S3 limit.
