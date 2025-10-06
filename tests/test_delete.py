from insta_images.services.image_service import upload_image, delete_image, get_image
import pytest


def test_delete_flow():
    metadata = {
        "image_id": "test-del-1",
        "user_id": "user-test",
        "filename": "test-del-1.jpg",
    }
    file_bytes = b"deleteme"
    upload_image(file_bytes, metadata)
    resp = delete_image("test-del-1")
    assert resp["status"] == "deleted"
    # after delete, get_image should raise
    with pytest.raises(Exception):
        get_image("test-del-1")
