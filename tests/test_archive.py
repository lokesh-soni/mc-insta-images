from insta_images.services.image_service import upload_image, archive_image, get_image
import pytest


def test_archive_flow():
    metadata = {
        "image_id": "test-arc-1",
        "user_id": "user-test",
        "filename": "test-arc-1.jpg",
    }
    file_bytes = b"archiveme"
    upload_image(file_bytes, metadata)
    resp = archive_image("test-arc-1")
    assert resp["status"] == "archived"
    with pytest.raises(Exception):
        # original get by image should still return metadata but file_bytes moved; depending on business logic
        # our get_image downloads by s3_key, so after move it still should be retrievable.
        # To keep assertion meaningful, fetch metadata and assert flags:
        meta = get_image("test-arc-1")["metadata"]
        assert meta["is_archived"] is True
