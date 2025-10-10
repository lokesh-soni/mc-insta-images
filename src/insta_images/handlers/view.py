
from insta_images.services.image_service import get_image
from insta_images.utils.exceptions import ImageNotFound, InvalidSearchFilter
from insta_images.utils.helpers import response_builder


def lambda_handler(event, context):
    try:
        image_id = event.get("pathParameters", "{}").get("id")
        if image_id:
            print(image_id)
            resp = get_image(image_id)
            print(resp)
            if resp:
                return response_builder(200, response_body=resp)
        else:
            raise InvalidSearchFilter("Missing Images Id in path")
        
    except InvalidSearchFilter as err:
        return response_builder(422, response_body=str(err))
    except ImageNotFound:
        return response_builder(404, response_body="Image Not Found !!")
    except Exception as e:
        return response_builder(400, response_body=str(e))
    