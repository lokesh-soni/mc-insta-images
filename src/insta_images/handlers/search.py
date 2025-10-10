import json

from insta_images.services.image_service import search_images
from insta_images.utils.constants import SUPPORTED_FILTER_KEY
from insta_images.utils.exceptions import InvalidSearchFilter
from insta_images.utils.logger import logger


def lambda_handler(event, context):
    req_body = event.get('body', {})
    try:
        validate_search_filters(req_body)
        items = search_images(req_body.get('filters'))
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"result": items, "totalCount": len(items)}),
        }
    except InvalidSearchFilter as invalid_filter_msg:
        logger.exception(invalid_filter_msg)
        return {"statusCode": 422, "body": invalid_filter_msg}
    except Exception as e:
        logger.exception("search handler error")
        return {"statusCode": 500, "body": str(e)}


def validate_search_filters(req_body):
    filters = req_body.get('filters')
    if not filters:
        raise InvalidSearchFilter("'filters' key is missing !!")
    if not isinstance(filters, dict):
        raise InvalidSearchFilter("Search filter object should be a json !!")
    unsupported_filter_keys = []
    for key in filters.keys():
        if key not in SUPPORTED_FILTER_KEY:
            unsupported_filter_keys.append(key)
    if unsupported_filter_keys:
        raise InvalidSearchFilter(f"Unsupported filter keys: {','.join(unsupported_filter_keys)}")
            