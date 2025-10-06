#!/bin/bash
set -e

# ------------------------------
# Configuration
# ------------------------------
COMPOSE_FILE=docker-compose.yml
CONTAINER_NAME=localstack_main
AWS_ENDPOINT=http://localhost:4566

S3_BUCKET=insta-images
S3_LIFECYCLE_FILE=src/resources/s3_lifecycle.json

DYNAMO_TABLE=Images
DYNAMO_SCHEMA_FILE=src/resources/images_table.json

# ------------------------------
# Check if container is running
# ------------------------------
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" == "" ]; then
    echo "LocalStack container not running. Starting via docker-compose..."
    docker-compose -f $COMPOSE_FILE up -d
    echo "Waiting 10 seconds for LocalStack to initialize..."
    sleep 10
else
    echo "LocalStack container $CONTAINER_NAME already running."
fi

# ------------------------------
# Create S3 bucket if not exists
# ------------------------------
if ! aws --endpoint-url=$AWS_ENDPOINT s3 ls "s3://$S3_BUCKET" 2>&1 | grep -q "$S3_BUCKET"; then
    echo "Creating S3 bucket: $S3_BUCKET"
    aws --endpoint-url=$AWS_ENDPOINT s3 mb s3://$S3_BUCKET
else
    echo "S3 bucket $S3_BUCKET already exists. Skipping creation."
fi

# Apply lifecycle policy if JSON exists
if [ -f "$S3_LIFECYCLE_FILE" ]; then
    echo "Applying S3 lifecycle policy from $S3_LIFECYCLE_FILE"
    aws --endpoint-url=$AWS_ENDPOINT s3api put-bucket-lifecycle-configuration \
        --bucket $S3_BUCKET \
        --lifecycle-configuration file://$S3_LIFECYCLE_FILE
fi

# ------------------------------
# Create DynamoDB table if not exists
# ------------------------------
if ! aws --endpoint-url=$AWS_ENDPOINT dynamodb describe-table --table-name $DYNAMO_TABLE >/dev/null 2>&1; then
    echo "Creating DynamoDB table: $DYNAMO_TABLE"
    aws --endpoint-url=$AWS_ENDPOINT dynamodb create-table \
        --cli-input-json file://$DYNAMO_SCHEMA_FILE
else
    echo "DynamoDB table $DYNAMO_TABLE already exists. Skipping creation."
fi

echo "LocalStack setup completed!"
echo "S3 Bucket: $S3_BUCKET"
echo "DynamoDB Table: $DYNAMO_TABLE"
echo "AWS Endpoint: $AWS_ENDPOINT"
