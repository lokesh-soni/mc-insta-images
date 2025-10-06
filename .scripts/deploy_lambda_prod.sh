#!/bin/bash
set -e

ENVIRONMENT=prod
HANDLER_NAME=${1:-upload}

AWS_ACCOUNT_ID=000000000000
AWS_REGION=us-east-1
AWS_PROFILE=loki
AWS_ENDPOINT=""  # public AWS endpoints

LAMBDA_NAME="${HANDLER_NAME}_image"
ZIP_FILE="dist/${LAMBDA_NAME}.zip"
ROLE_ARN="arn:aws:iam::$AWS_ACCOUNT_ID:role/lambda-execution-role"

function aws_cmd() { aws --profile "$AWS_PROFILE" "$@"; }

mkdir -p dist
rm -f $ZIP_FILE
cd src
zip -r ../$ZIP_FILE insta_images
cd -

if aws_cmd lambda get-function --function-name $LAMBDA_NAME >/dev/null 2>&1; then
    echo "Updating Lambda $LAMBDA_NAME..."
    aws_cmd lambda update-function-code --function-name $LAMBDA_NAME --zip-file fileb://$ZIP_FILE
    aws_cmd lambda update-function-configuration --function-name $LAMBDA_NAME \
        --handler "insta_images.handlers.${HANDLER_NAME}.lambda_handler" --runtime python3.10 --role $ROLE_ARN
else
    echo "Creating Lambda $LAMBDA_NAME..."
    aws_cmd lambda create-function --function-name $LAMBDA_NAME --runtime python3.10 \
        --role $ROLE_ARN --handler "insta_images.handlers.${HANDLER_NAME}.lambda_handler" \
        --zip-file fileb://$ZIP_FILE
fi

echo "Lambda deployed: $LAMBDA_NAME (prod)"
