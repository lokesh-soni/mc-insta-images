import json
import os
import uuid
import boto3
import logging
from insta_images.services.image_service import db
from insta_images.utils.exceptions import InvalidMetadata

logger = logging.getLogger()
logger.setLevel(logging.INFO)

S3_BUCKET = os.getenv("S3_BUCKET", "insta-images")
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:4566")

s3_client = boto3.client("s3", endpoint_url=S3_ENDPOINT, region_name="us-east-1")


def lambda_handler(event, context):
    try:
        req_body = json.loads(event.get("body", "{}"))
        image_id = req_body.get("image_id") or str(uuid.uuid4())
        user_id = req_body.get("user_id")
        if not user_id:
            raise InvalidMetadata("user_id is required")

        s3_key = f"images/active/{image_id}.jpg"
        image = {
            "image_id": image_id,
            "user_id": user_id,
            "s3_key": s3_key,
            "tags": req_body.get("tags", []),
            "additional_info": req_body.get("additional_info", {}),
            "is_live": True,
            "is_archived": False,
            "is_deleted": False,
        }

        presigned_url = s3_client.generate_presigned_url(
            "put_object",
            Params={"Bucket": S3_BUCKET, "Key": s3_key, "ContentType": "image/jpeg"},
            ExpiresIn=3600,
        )
        if presigned_url:
            db.put_item(image)
            logger.info(
                "Generated presigned URL for image_id %s at s3_key %s", image_id, s3_key
            )
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    {
                        "presigned_url": presigned_url,
                        "s3_key": s3_key,
                        "user_id": user_id,
                        "image_id": image_id,
                    }
                ),
            }
        else:
            raise Exception("Failed to generate pre-signed URL")
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)}),
        }
