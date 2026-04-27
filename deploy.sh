#!/bin/bash
set -euo pipefail

# Configuration
FUNCTION_NAME="zuna-grey-bbs"
ZIP_FILE="deployment_package.zip"
AWS_PROFILE="d301"
AWS_REGION="us-east-1"
CLOUDFRONT_ID="EVBJR6TDA3B8M"

echo "--- Zuna Grey deploy ---"

if ! command -v aws &> /dev/null; then
  echo "ERROR: aws CLI not found."; exit 1
fi

# 1. Package site + lambda handler
echo "Packaging..."
rm -f "$ZIP_FILE"
zip -qr "$ZIP_FILE" \
  lambda_function.py \
  index.html press.html terminal.html \
  assets
echo "Package: $(du -h "$ZIP_FILE" | cut -f1)"

# 2. Push to Lambda
echo "Updating Lambda '$FUNCTION_NAME'..."
aws lambda update-function-code \
  --function-name "$FUNCTION_NAME" \
  --zip-file "fileb://$ZIP_FILE" \
  --profile "$AWS_PROFILE" --region "$AWS_REGION" \
  --no-cli-pager --output text > /dev/null
echo "Lambda updated."

# 3. Wait for code update to finish propagating
echo "Waiting for Lambda to be Active..."
aws lambda wait function-updated-v2 \
  --function-name "$FUNCTION_NAME" \
  --profile "$AWS_PROFILE" --region "$AWS_REGION" 2>/dev/null || true

# 4. Invalidate CloudFront so visitors see the new content immediately
echo "Invalidating CloudFront ($CLOUDFRONT_ID)..."
INVALIDATION_ID=$(aws cloudfront create-invalidation \
  --distribution-id "$CLOUDFRONT_ID" \
  --paths "/*" \
  --profile "$AWS_PROFILE" \
  --query 'Invalidation.Id' --output text)
echo "Invalidation: $INVALIDATION_ID (typically completes in 1-3 min)"

echo "Done. https://zunagrey.com"
