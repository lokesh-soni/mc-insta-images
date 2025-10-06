import logging
import os

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logger = logging.getLogger("insta_images")
logger.setLevel(LOG_LEVEL)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(LOG_LEVEL)
    fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ch.setFormatter(logging.Formatter(fmt))
    logger.addHandler(ch)
