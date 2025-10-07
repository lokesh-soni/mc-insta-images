import json
import uuid

from insta_images.services.s3_service import S3Service
from insta_images.services.dynamodb_service import DynamoDBService
from insta_images.utils.logger import logger
from insta_images.utils.exceptions import ImageNotFound

s3 = S3Service()
db = DynamoDBService()


def create_or_update_image(req_body: dict):
    image_id = req_body.get("image_id") or str(uuid.uuid4())
    user_id = req_body.get("user_id")

    is_live = req_body.get("is_live", True),
    is_archived = req_body.get("is_archived", False),
    is_deleted = req_body.get("is_deleted", False),

    if is_archived:
        s3_key = f"images/archived/{image_id}.jpg"
    elif is_deleted:
        s3_key = f"images/deleted/{image_id}.jpg"
    else:
        s3_key = f"images/active/{image_id}.jpg"
    image = {
        "image_id": image_id,
        "user_id": user_id,
        "s3_key": s3_key,
        "tags": req_body.get("tags", []),
        "additional_info": req_body.get("additional_info", {}),
        "is_live": is_live,
        "is_archived": is_archived,
        "is_deleted": is_deleted,
    }
    db.put_item(image)
    presigned_url = s3.get_signed_url(s3_key, "put_object")
    return json.dumps(
        {
            "presigned_url": presigned_url,
            "s3_key": s3_key,
            "user_id": user_id,
            "image_id": image_id,
        }
    )


def list_images(user_id: str = None):
    return db.list_items(user_id=user_id)


def get_image(image_id: str):
    item = db.get_item(image_id)
    if not item:
        raise ImageNotFound(image_id)
    
    if item.get("s3_key"):
        signed_url = s3.get_signed_url(item.get("s3_key"))
        return {"metadata": item, "signed_url": signed_url}
        

def delete_image(image_id: str):
    item = db.get_item(image_id)
    if not item:
        raise ImageNotFound(image_id)
    old_key = item.get("s3_key")
    filename = old_key.split('/')[-1]
    dest = s3.build_deleted_key(filename)
    s3.move_file(old_key, dest)
    item["is_deleted"] = True
    item["is_live"] = False
    item["s3_key"] = dest
    db.put_item(item)
    logger.info("delete_image completed for %s", image_id)


def search_images(filters):
    gross_list = []
    if filters.get("user_id"):
        gross_list = db.query_by_user(user_id=filters.get("user_id"))
    else:
        
        pass