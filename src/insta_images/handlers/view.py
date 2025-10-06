
from insta_images.services.image_service import get_image
from insta_images.utils.exceptions import ImageNotFound


def lambda_handler(event, context):
    
    try:
        
        image_id = event.get("pathParameters", "{}").get("id")
        if not image_id:
            return {"statusCode": 400, "body": "Missing Images Id in path"}
        resp = get_image(image_id)
        if resp:
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": resp,
            }
    except ImageNotFound:
        return {
            "statusCode": 404,
            "headers": {"Content-Type": "application/json"},
            "body": "Image Not Found !!",
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": str(e),
        }
