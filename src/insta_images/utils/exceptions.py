class ImageServiceError(Exception):
    pass


class ImageNotFound(ImageServiceError):
    pass


class InvalidMetadata(ImageServiceError):
    pass
