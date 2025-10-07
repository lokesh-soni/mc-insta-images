import logging

from insta_images.utils.config import get_env


LOG_LEVEL = get_env("LOG_LEVEL", "INFO").upper()
logger = logging.getLogger(get_env("APP_NAME"))
logger.setLevel(LOG_LEVEL)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(LOG_LEVEL)
    fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ch.setFormatter(logging.Formatter(fmt))
    logger.addHandler(ch)
