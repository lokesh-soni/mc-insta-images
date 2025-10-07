from insta_images.utils.config import load_config
from insta_images.utils.exceptions import ImageNotFound
from insta_images.utils.logger import logger


def lambda_handler(event, context):
    load_config(event.get('requestContext').get('stage'))
    image_id = event.get("pathParameters", "{}").get("id")
    if not image_id:
        return {"statusCode": 400, "body": "Missing Images Id in path"}
    try:
        update_image(image_id)
        return {"statusCode": 200, "body": "Archived !!"}
    except ImageNotFound:
        return {"statusCode": 404, "body": "Image not found"}
    except Exception:
        logger.exception("delete handler error")
        return {"statusCode": 400, "body": "Something went wrong"}
