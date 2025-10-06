import json

from insta_images.services.image_service import search_images
from insta_images.utils.logger import logger


def lambda_handler(event, context):
    user_id = event.get("user_id")
    tag = event.get("tag")
    try:
        items = search_images(user_id=user_id, tag=tag)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"result": items, "totalCount": len(items)}),
        }
    except Exception as e:
        logger.exception("search handler error")
        return {"statusCode": 500, "body": str(e)}
