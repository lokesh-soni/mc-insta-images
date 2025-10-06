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

        # ensure bucket exists (safe for LocalStack)
        try:
            resp = self.client.list_buckets()
            exists = any(b["Name"] == self.bucket for b in resp.get("Buckets", []))
            if not exists:
                # For LocalStack, simple create_bucket works.
                try:
                    self.client.create_bucket(Bucket=self.bucket)
                except Exception:
                    # some regions require CreateBucketConfiguration; ignore if it fails in LocalStack
                    self.client.create_bucket(Bucket=self.bucket)
            logger.debug("S3Service ready, bucket=%s", self.bucket)
        except ClientError as e:
            logger.warning("Could not confirm/create bucket: %s", e)

    def upload_file(self, file_bytes: bytes, full_key: str) -> str:
        """Upload to S3. full_key should include the path prefix (e.g. images/active/xxx.jpg)."""
        self.client.put_object(Bucket=self.bucket, Key=full_key, Body=file_bytes)
        logger.info("Uploaded file to S3: %s/%s", self.bucket, full_key)
        return full_key

    def download_file(self, full_key: str) -> bytes:
        """Download object bytes by full key."""
        obj = self.client.get_object(Bucket=self.bucket, Key=full_key)
        data = obj["Body"].read()
        logger.info(
            "Downloaded file from S3: %s/%s (bytes=%d)",
            self.bucket,
            full_key,
            len(data),
        )
        return data

    def obj_exist(self, key: str) -> bool:
        """Check if an object exists in the S3 bucket."""
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as e:
            print(e)
            if e.response["Error"]["Code"] == "404":
                return False
            raise

    def move_file(self, src_full_key: str, dest_full_key: str):
        """Safely move (copy + delete) an object if it exists."""
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
        
    def get_download_signed_url(self, full_key: str):
        signed_url = full_key
        try:
            signed_url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": full_key},
                ExpiresIn=3600  # 1 hour
            )
            logger.info("Signed URL to download S3 object generated: %s", full_key)
            return signed_url
        except Exception as e:
            logger.error("Failed to Sign URL with error %s", str(e))
            return str(e)
        
    @staticmethod
    def build_active_key(filename: str):
        return f"{S3_PATH_ACTIVE}{filename}"

    @staticmethod
    def build_archived_key(filename: str):
        return f"{S3_PATH_ARCHIVED}{filename}"

    @staticmethod
    def build_deleted_key(filename: str):
        return f"{S3_PATH_DELETED}{filename}"
