import os


def get_env(name: str, default=None, required: bool = False):
    v = os.environ.get(name, default)
    if required and v is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return v
