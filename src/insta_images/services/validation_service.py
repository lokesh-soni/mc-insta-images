import json
import os
from jsonschema import validate, ValidationError

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "resources", "schema.json")
with open(SCHEMA_PATH) as f:
    SCHEMAS = json.load(f)


def validate_request(data, schema_name):
    schema = SCHEMAS[schema_name]
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        raise ValueError(f"Validation failed: {e.message}")
