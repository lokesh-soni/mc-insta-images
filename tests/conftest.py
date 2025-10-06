import os
import time
import json
import boto3
import pytest
from dotenv import load_dotenv
from pathlib import Path

# Load env for tests (dev)
load_dotenv("src/resources/.env.common")
load_dotenv("src/resources/.env.dev")

ENDPOINT = os.environ.get("ENDPOINT_URL")
REGION = os.environ.get("AWS_REGION", "us-east-1")
S3_BUCKET = os.environ.get("S3_BUCKET", "images")
TABLE = os.environ.get("DYNAMO_TABLE", "Images")


@pytest.fixture(scope="session", autouse=True)
def ensure_infra():
    # create bucket
    s3 = boto3.client("s3", endpoint_url=ENDPOINT, region_name=REGION)
    buckets = [b["Name"] for b in s3.list_buckets().get("Buckets", [])]
    if S3_BUCKET not in buckets:
        try:
            s3.create_bucket(Bucket=S3_BUCKET)
        except Exception:
            s3.create_bucket(Bucket=S3_BUCKET)

    # create table if not exists using resource file
    dynamo = boto3.client("dynamodb", endpoint_url=ENDPOINT, region_name=REGION)
    existing = dynamo.list_tables().get("TableNames", [])
    if TABLE not in existing:
        schema_path = Path("src/resources/images_table.json")
        with open(schema_path) as f:
            schema = json.load(f)
        dynamo.create_table(**schema)
        # wait until active (simple wait)
        for _ in range(20):
            resp = dynamo.describe_table(TableName=TABLE)
            if resp["Table"]["TableStatus"] == "ACTIVE":
                break
            time.sleep(0.5)
    yield
    # no teardown to avoid accidental data wipes in dev; tests can be idempotent
