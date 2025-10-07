from insta_images.utils.config import load_config


def init(request_context: dict):
    load_config(request_context.get('stage'))
    