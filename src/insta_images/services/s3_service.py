import boto3
from botocore.exceptions import ClientError
from insta_images.utils.config import get_env
from insta_images.utils.constants import (
    S3_PATH_ACTIVE,
    S3_PATH_ARCHIVED,
    S3_PATH_DELETED,
)
from insta_images.utils.logger import logger


class S3Service:
    def __init__(self):
        endpoint = get_env("ENDPOINT_URL", None)
        region = get_env("AWS_REGION", None)
        self.bucket = get_env("S3_BUCKET", "insta-images")
        if endpoint:
            self.client = boto3.client("s3", endpoint_url=endpoint, region_name=region)
        else:
            self.client = boto3.client("s3", region_name=region)
            logger.debug("S3Service ready, bucket=%s", self.bucket)

    def obj_exist(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise

    def upload_file(self, file_bytes: bytes, full_key: str) -> str:
        self.client.put_object(Bucket=self.bucket, Key=full_key, Body=file_bytes)
        logger.info("Uploaded file to S3: %s/%s", self.bucket, full_key)
        return full_key

    def move_file(self, src_full_key: str, dest_full_key: str):
        if self.obj_exist(src_full_key):
            copy_source = {"Bucket": self.bucket, "Key": src_full_key}
            self.client.copy_object(
                Bucket=self.bucket, Key=dest_full_key, CopySource=copy_source
            )
            self.client.delete_object(Bucket=self.bucket, Key=src_full_key)
            logger.info(f"Moved S3 object: {src_full_key} -> {dest_full_key}")
        else:
            logger.warning(f"S3 object does not exist: {src_full_key}")

    def delete_file(self, full_key: str):
        self.client.delete_object(Bucket=self.bucket, Key=full_key)
        logger.info("Deleted S3 object: %s", full_key)
        
    def get_signed_url(self, full_key: str, action: str = "get_object"):
        return self.client.generate_presigned_url(
            action,
            Params={"Bucket": self.bucket, "Key": full_key, "ContentType": "image/jpeg"},
            ExpiresIn=3600
        )
    
    @staticmethod
    def build_active_key(filename: str):
        return f"{S3_PATH_ACTIVE}{filename}"

    @staticmethod
    def build_archived_key(filename: str):
        return f"{S3_PATH_ARCHIVED}{filename}"

    @staticmethod
    def build_deleted_key(filename: str):
        return f"{S3_PATH_DELETED}{filename}"
