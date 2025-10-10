import boto3
from boto3.dynamodb.conditions import Key, Attr
from insta_images.utils.config import get_env
from insta_images.utils.logger import logger


class DynamoDBService:
    def __init__(self):
        endpoint = get_env("ENDPOINT_URL", None)
        region = get_env("AWS_REGION", None)
        self.table_name = get_env("DYNAMO_TABLE", "Images")
        if endpoint:
            self.dynamodb = boto3.resource(
                "dynamodb", region_name=region, endpoint_url=endpoint
            )
        else:
            self.dynamodb = boto3.resource("dynamodb", region_name=region)
        self.table = self.dynamodb.Table(self.table_name)
        logger.debug("DynamoDBService connected to table %s", self.table_name)

    def get_item(self, image_id: str):
        resp = self.table.get_item(Key={"image_id": image_id})
        item = resp.get("Item")
        logger.debug("DynamoDB get_item %s -> %s", image_id, bool(item))
        return item

    def put_item(self, item):
        payload = item if isinstance(item, dict) else item.__dict__
        self.table.put_item(Item=payload)
        logger.info("DynamoDB put_item: %s", payload.get("image_id"))

    def delete_item(self, image_id: str):
        self.table.delete_item(Key={"image_id": image_id})
        logger.info("DynamoDB delete_item: %s", image_id)

    def list_items(self, user_id: str = None):
        items = []
        if user_id:
            try:
                resp = self.table.query(
                    IndexName="user_created_index",
                    KeyConditionExpression=Key("user_id").eq(user_id),
                )
                items = resp.get("Items", [])
            except Exception as e:
                logger.warning("Query by user failed: %s - falling back to scan", e)
                resp = self.table.scan(FilterExpression=Attr("user_id").eq(user_id))
                items = resp.get("Items", [])
        else:
            resp = self.table.scan()
            items = resp.get("Items", [])

        logger.info("list_items returned %d items (user_id=%s)", len(items), user_id)
        return items

    def query_by_user(self, user_id: str):
        return self.list_items(user_id=user_id)

    def query_by_filters(self, user_id: str):
        return self.list_items(user_id=user_id)
