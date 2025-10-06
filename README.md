## ==========================
## =========== S3 ===========
## ==========================

## Create
`aws --endpoint-url=http://localhost:4566 s3 mb s3://insta-images`

## List Buckets
`aws --endpoint-url=http://localhost:4566 s3 ls`
## List Objects
`aws --endpoint-url=http://localhost:4566 s3 ls insta-images`

## Create Lifecycle Policies
`aws --endpoint-url=http://localhost:4566 s3api put-bucket-lifecycle-configuration --bucket insta-images --lifecycle-configuration file://.scripts/_includes/s3_lifecycle.json`

## List Lifecycle Policies
`aws --endpoint-url=http://localhost:4566 s3api get-bucket-lifecycle-configuration --bucket insta-images`

## ==========================
## ======== DynamoDB ========
## ==========================

## Create

`aws --endpoint-url=http://localhost:4566 dynamodb create-table --cli-input-json file://.scripts/_includes/images_table.json --deletion-protection-enabled`

## List
`aws --endpoint-url=http://localhost:4566 dynamodb describe-table --table-name Images`

## View Objects
`aws --endpoint-url=http://localhost:4566 dynamodb scan --table-name Images`

## ==========================
## ========= Lambda =========
## ==========================


## Create
`bash .scripts/deploy_lambda_dev.sh`

## List 
`aws --endpoint-url=http://localhost:4566 lambda list-functions`

## Delete
`aws --profile localstack --endpoint-url http://localhost:4566 lambda list-functions --query "Functions[].FunctionName" --output text | xargs -n1 -r aws --profile localstack --endpoint-url http://localhost:4566 lambda delete-function --function-name`

## ==========================
## ======= apiGateway =======
## ==========================

## API-Id
`API_ID=$(aws --profile localstack --endpoint-url http://localhost:4566 apigateway get-rest-apis --query "items[?name=='InstaImageAPI'].id" --output text)`

## Create
`bash .scripts/create_api_dev.sh`

## List resources and their HTTP methods
`aws --profile localstack --endpoint-url http://localhost:4566 apigateway get-resources --rest-api-id $API_ID --query "items[*].[path, resourceMethods]" --output json`

## Delete 
`aws --profile localstack --endpoint-url http://localhost:4566 apigateway get-rest-apis --query "items[].id" --output text | xargs -n1 -r aws --profile localstack --endpoint-url http://localhost:4566 apigateway delete-rest-api --rest-api-id`

====
