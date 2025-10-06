from insta_images.services.image_service import delete_image
from insta_images.utils.exceptions import ImageNotFound
from insta_images.utils.logger import logger


def lambda_handler(event, context):
    image_id = event.get("pathParameters", "{}").get("id")
    if not image_id:
        return {"statusCode": 400, "body": "Missing Images Id in path"}
    try:
        delete_image(image_id)
        return {"statusCode": 204, "body": "Deleted !!"}
    except ImageNotFound:
        return {"statusCode": 404, "body": "Image not found"}
    except Exception:
        logger.exception("delete handler error")
        return {"statusCode": 400, "body": "Something went wrong"}
