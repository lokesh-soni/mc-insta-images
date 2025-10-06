#!/bin/bash
set -e
ENVIRONMENT=prod
AWS_ACCOUNT_ID=000000000000
AWS_REGION=us-east-1
AWS_PROFILE=loki
AWS_ENDPOINT=""
API_NAME=InstaImageAPI
API_STAGE=prod

function aws_cmd() { aws --profile "$AWS_PROFILE" "$@"; }

API_ID=$(aws_cmd apigateway get-rest-apis --query "items[?name=='$API_NAME'].id" --output text)
if [ -z "$API_ID" ]; then
    API_ID=$(aws_cmd apigateway create-rest-api --name $API_NAME --query "id" --output text)
fi

ROOT_ID=$(aws_cmd apigateway get-resources --rest-api-id $API_ID --query "items[?path=='/'].id" --output text)

declare -a ENDPOINTS=(
    "/images POST upload_image"
    "/images GET list_image"
    "/images/{id} GET view_image"
    "/images/{id} DELETE delete_image"
)

for e in "${ENDPOINTS[@]}"; do
    read -r path method lambda <<< "$e"
    # create_method_integration logic here
done

aws_cmd apigateway create-deployment --rest-api-id "$API_ID" --stage-name "$API_STAGE"
echo "Prod API endpoint: https://<api-id>.execute-api.$AWS_REGION.amazonaws.com/$API_STAGE/"
