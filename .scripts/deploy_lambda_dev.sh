#!/bin/bash
set -e

# ------------------------------
# Config
# ------------------------------
ENVIRONMENT=dev
HANDLER_NAME=${1:-all}  # upload, view, delete, list, archive, or all

AWS_ACCOUNT_ID=000000000000
AWS_REGION=us-east-1
AWS_PROFILE=localstack
AWS_ENDPOINT="http://localhost:4566"

ROLE_ARN="arn:aws:iam::$AWS_ACCOUNT_ID:role/lambda-execution-role"
SRC_DIR="src"
DIST_DIR="dist"

# ------------------------------
# Handler list
# ------------------------------
HANDLERS=("upload" "view" "delete" "list" "archive")

# ------------------------------
# Helpers
# ------------------------------
function aws_cmd() {
    aws --profile "$AWS_PROFILE" --endpoint-url "$AWS_ENDPOINT" "$@"
}

function create_zip() {
    mkdir -p "$DIST_DIR"
    local zip_file="$DIST_DIR/${1}_image.zip"
    rm -f "$zip_file"
    (cd "$SRC_DIR" && zip -r "../$zip_file" insta_images >/dev/null)
    echo "$zip_file"
}

function lambda_exists() {
    aws_cmd lambda get-function --function-name "$1" >/dev/null 2>&1
}

function deploy_single_lambda() {
    local handler="$1"
    local lambda_name="${handler}_image"
    local zip_file
    zip_file=$(create_zip "$handler")

    echo "🚀 Deploying Lambda: $lambda_name"

    if lambda_exists "$lambda_name"; then
        echo "Updating existing Lambda..."
        aws_cmd lambda update-function-code \
            --function-name "$lambda_name" \
            --zip-file "fileb://$zip_file" >/dev/null 2>&1

        aws_cmd lambda update-function-configuration \
            --function-name "$lambda_name" \
            --handler "insta_images.handlers.${handler}.lambda_handler" \
            --runtime python3.10 \
            --role "$ROLE_ARN" >/dev/null 2>&1

        # Trigger dummy invoke for LocalStack to initialize $LATEST
        aws_cmd lambda invoke --function-name "$lambda_name" --payload {} /dev/null || true
    else
        echo "Creating new Lambda..."
        aws_cmd lambda create-function \
            --function-name "$lambda_name" \
            --runtime python3.10 \
            --role "$ROLE_ARN" \
            --handler "insta_images.handlers.${handler}.lambda_handler" \
            --zip-file "fileb://$zip_file" >/dev/null 2>&1
    fi

    echo "✅ Lambda deployed: $lambda_name"
    echo
}

# ------------------------------
# Main
# ------------------------------
if [ "$HANDLER_NAME" == "all" ]; then
    echo "Deploying all handlers: ${HANDLERS[*]}"
    for h in "${HANDLERS[@]}"; do
        deploy_single_lambda "$h"
    done
else
    deploy_single_lambda "$HANDLER_NAME"
fi

echo "🎉 All deployments complete for environment: $ENVIRONMENT"
