import os
import argparse
from dotenv import load_dotenv
from insta_images.handlers import upload

parser = argparse.ArgumentParser(description="Run Instagram Lambda handlers")
parser.add_argument(
    "--env", type=str, default="dev", help="Environment: dev/staging/prod"
)
parser.add_argument(
    "--handler", type=str, required=True, help="Handler: upload/list/view/delete"
)
args = parser.parse_args()

# Load environment variables
load_dotenv("src/resources/.env.common")
env_file = f"src/resources/.env.{args.env}"
if os.path.exists(env_file):
    load_dotenv(env_file)
else:
    raise FileNotFoundError(f"{env_file} not found")

# Map handlers
handler_map = {
    "upload": upload.lambda_handler,
    "list": list_images.lambda_handler,
    "view": view_image.lambda_handler,
    "delete": delete_image.lambda_handler,
}

handler = handler_map.get(args.handler)
if not handler:
    raise ValueError(f"Unknown handler: {args.handler}")

# Dummy event/context for testing
event = {}
context = {}
response = handler(event, context)
print(response)
