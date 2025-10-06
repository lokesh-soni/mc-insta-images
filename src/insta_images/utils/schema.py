import json
from jsonschema import validate
from pathlib import Path

schema_file = Path("src/resources/image_upload_schema.json")
with open(schema_file) as f:
    IMAGE_UPLOAD_SCHEMA = json.load(f)


def validate_upload_payload(payload: dict):
    validate(instance=payload, schema=IMAGE_UPLOAD_SCHEMA)
