import base64
from io import BytesIO
from PIL import Image
import requests


def url_to_pil_image(url: str):
    if not isinstance(url, str):
        return None

    if url.startswith("data:image"):
        base64_str_index = url.find("base64,") + len("base64,")
        image_data = base64.b64decode(url[base64_str_index:])
        image = Image.open(BytesIO(image_data))
    else:
        # add 10 seconds timeout
        response = requests.get(url, timeout=10)
        image = Image.open(BytesIO(response.content))

    return image


def url_to_cv2_image(url: str):
    """Converts a URL to a cv2 image. Remember to install cv2 and numpy."""
    import cv2
    import numpy as np

    if not isinstance(url, str):
        return None

    if url.startswith("data:image"):
        base64_str_index = url.find("base64,") + len("base64,")
        image_data = base64.b64decode(url[base64_str_index:])
        image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
    else:
        response = requests.get(url)
        image = cv2.imdecode(
            np.frombuffer(response.content, np.uint8), cv2.IMREAD_COLOR
        )

    return image
