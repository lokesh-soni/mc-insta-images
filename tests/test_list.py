from insta_images.services.image_service import list_images


def test_list_images(db_client):
    items = list_images(user_id="user1")
    assert isinstance(items, list)
