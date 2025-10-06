from insta_images.services.s3_service import S3Service
from insta_images.services.dynamodb_service import DynamoDBService
from insta_images.services.models import Image
from insta_images.utils.logger import logger
from insta_images.utils.exceptions import ImageNotFound, InvalidMetadata

s3 = S3Service()
db = DynamoDBService()


def upload_image(file_bytes: bytes, metadata: dict):
    # metadata should include image_id, user_id and optional 'filename' or 's3_key'
    image_id = metadata.get("image_id")
    user_id = metadata.get("user_id")
    if not image_id or not user_id:
        raise InvalidMetadata("image_id and user_id are required")

    filename = metadata.get("filename", f"{image_id}.jpg")
    # create full s3 key
    s3_key = metadata.get("s3_key") or s3.build_active_key(filename)

    image = Image(
        image_id=image_id,
        user_id=user_id,
        s3_key=s3_key,
        tags=metadata.get("tags", []),
        additional_info=metadata.get("additional_info", {}),
    )

    s3.upload_file(file_bytes, image.s3_key)
    db.put_item(image)
    logger.info("upload_image completed for %s", image_id)
    return {"image_id": image_id, "s3_key": image.s3_key}


def list_images(user_id: str = None, tag: str = None):
    return db.list_items(user_id=user_id, tag=tag)


def get_image(image_id: str):
    item = db.get_item(image_id)
    if not item:
        raise ImageNotFound(image_id)
    
    if item.get("s3_key"):
        signed_url = s3.get_download_signed_url(item.get("s3_key"))
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


def search_images(**kwargs):
    pass