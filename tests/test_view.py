from insta_images.services.image_service import upload_image, get_image
import base64


def test_view_existing_image():
    metadata = {
        "image_id": "test-view-1",
        "user_id": "user-test",
        "filename": "test-view-1.jpg",
    }
    file_bytes = b"abc123"
    upload_image(file_bytes, metadata)
    res = get_image("test-view-1")
    assert "metadata" in res
    assert res["metadata"]["image_id"] == "test-view-1"
    assert res["file_bytes"] == b"abc123"
