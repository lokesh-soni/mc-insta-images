#!/bin/bash
set -e

# ------------------------------
# Config & constants
# ------------------------------
ENVIRONMENT=dev
AWS_ACCOUNT_ID=000000000000  # replace with your prod account id
AWS_REGION=us-east-1

LOCALSTACK_PROFILE=localstack
PROD_PROFILE=loki

AWS_PROFILE=$LOCALSTACK_PROFILE
AWS_ENDPOINT="http://localhost:4566"

ROLE_ARN="arn:aws:iam::$AWS_ACCOUNT_ID:role/lambda-execution-role"

API_NAME=InstaImageAPI
API_STAGE=dev


function aws_cmd() {
    aws --profile "$AWS_PROFILE" ${AWS_ENDPOINT:+--endpoint-url $AWS_ENDPOINT} "$@"
}

function get_lambda() {
    upload_image "$@"
}

# ------------------------------
# API Gateway management
# ------------------------------

function get_api_id() {
    aws_cmd apigateway get-rest-apis --query "items[?name=='$API_NAME'].id" --output text
}

function create_api_if_not_exists() {
    local api_id=$(get_api_id)
    if [ -z "$api_id" ]; then
        api_id=$(aws_cmd apigateway create-rest-api --name $API_NAME --query "id" --output text)

        # Retry until get-resources succeeds
        local retries=5
        local count=0
        while ! aws_cmd apigateway get-resources --rest-api-id $api_id >/dev/null 2>&1; do
            ((count++))
            if [ $count -ge $retries ]; then
                exit 1
            fi
            sleep 1
        done
    fi
    echo "$api_id"
}


function get_root_id() {
    local api_id=$1
    aws_cmd apigateway get-resources --rest-api-id $api_id --query "items[?path=='/'].id" --output text
}

# ------------------------------
# Create method + integration for a resource path
# ------------------------------
# Parameters:
#   $1 = REST API ID
#   $2 = Full path (e.g., /images or /images/{id})
#   $3 = HTTP method (GET, POST, DELETE)
function create_method_integration() {
    local api_id=$1
    local full_path=$2
    local http_method=$3
    local lambda_func=$4

    # Split path into segments
    IFS='/' read -ra segments <<< "${full_path#/}"  # remove leading /
    local parent_id
    parent_id=$(get_root_id "$api_id")             # start from root

    for segment in "${segments[@]}"; do
        # Check if resource exists under parent
        resource_id=$(aws_cmd apigateway get-resources --rest-api-id "$api_id" \
            --query "items[?pathPart=='$segment' && parentId=='$parent_id'].id" --output text)

        # If not exists, create it
        if [ -z "$resource_id" ]; then
            resource_id=$(aws_cmd apigateway create-resource \
                --rest-api-id "$api_id" \
                --parent-id "$parent_id" \
                --path-part "$segment" \
                --query "id" --output text)
            echo "Created resource segment '$segment' with ID $resource_id"
        fi

        # Move to next parent
        parent_id=$resource_id
    done

    # The final resource_id is the one for this full_path
    final_resource_id=$parent_id

    # Check if method exists
    if ! aws_cmd apigateway get-method --rest-api-id "$api_id" \
        --resource-id "$final_resource_id" --http-method "$http_method" >/dev/null 2>&1; then

        echo "Creating $http_method method for $full_path"
        aws_cmd apigateway put-method \
            --rest-api-id "$api_id" --resource-id "$final_resource_id" \
            --http-method "$http_method" --authorization-type "NONE"

        aws_cmd apigateway put-integration \
            --rest-api-id "$api_id" --resource-id "$final_resource_id" \
            --http-method "$http_method" --type AWS_PROXY \
            --integration-http-method POST \
            --uri "arn:aws:apigateway:$AWS_REGION:lambda:path/2015-03-31/functions/arn:aws:lambda:$AWS_REGION:$AWS_ACCOUNT_ID:function:$lambda_func/invocations"
    fi
}

# ------------------------------
# Deploy all API endpoints (idempotent)
# ------------------------------
function deploy_api() {
    local api_id=$(create_api_if_not_exists)
    local root_id=$(get_root_id "$api_id")

    echo "Deploying API endpoints..."

    # Create all endpoints
    create_method_integration "$api_id" "/images" "POST" "upload_image"
    create_method_integration "$api_id" "/images" "GET" "list_image"
    create_method_integration "$api_id" "/images/{id}" "GET" "view_image"
    create_method_integration "$api_id" "/images/{id}" "DELETE" "delete_image"

    # Deploy stage
    echo "Deploying API Gateway stage: $API_STAGE"
    aws_cmd apigateway create-deployment --rest-api-id "$api_id" --stage-name "$API_STAGE"

    echo "Dev API endpoint: http://localhost:4566/restapis/$api_id/$API_STAGE/_user_request_/"
}

deploy_api
