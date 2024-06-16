import base64
import io
import mimetypes
import os
from typing import Dict, Union
from pydantic import BaseModel, Field
import requests
from fastapi import Response as FastAPIResponse

from .types import ContentType, ValueElement
from .image_conversion_utils import url_to_cv2_image, url_to_pil_image
from .constants import (
    DEFAULT_IMAGE_FORMAT,
    DEFAULT_IMAGE_MIME_TYPE,
)
from PIL import Image
import numpy as np


ContentElementContent = Union[str, bytes, Image.Image, np.ndarray]


class ContentElement(ValueElement):
    value: ContentElementContent


ContentsDictValue = Union[ContentElementContent, ContentElement]

ContentsDict = Dict[ContentType, ContentsDictValue]


class Content(BaseModel):
    contents: ContentsDict = Field(
        description="Dictionary mapping ContentType to content as str (URL, data URL-base64, or path), bytes, PIL Image, or NumPy array"
    )

    class Config:
        arbitrary_types_allowed = True

    def get_content(self, content_type: ContentType) -> ContentsDictValue:
        content = self.contents.get(content_type)

        if content is None:
            raise ValueError(f"No content found for content type: {content_type}")

        return content

    def get_cleaned_content(self, content_type: ContentType) -> ContentElementContent:
        content = self.get_content(content_type)
        if isinstance(content, ContentElement):
            return content.value
        return content

    def has_content(self, content_type: ContentType) -> bool:
        return content_type in self.contents

    def to_response(self, content_type: ContentType) -> FastAPIResponse:
        content = self.get_cleaned_content(content_type)

        if isinstance(content, (Image.Image, np.ndarray)):
            buffered = io.BytesIO()
            if isinstance(content, Image.Image):
                content.save(buffered, format=DEFAULT_IMAGE_FORMAT)
            else:
                Image.fromarray(content).save(buffered, format=DEFAULT_IMAGE_FORMAT)
            content_data = buffered.getvalue()
            return FastAPIResponse(
                content=content_data,
                media_type=DEFAULT_IMAGE_MIME_TYPE,
            )
        elif isinstance(content, str):
            if content.startswith(("http://", "https://")):
                response = requests.get(content)
                return FastAPIResponse(
                    content=response.content,
                    media_type=response.headers["Content-Type"],
                )
            elif content.startswith("data:"):
                header, encoded = content.split(",", 1)
                media_type = header.split(":")[1].split(";")[0]
                content = base64.b64decode(encoded)
                return FastAPIResponse(content=content, media_type=media_type)
            elif os.path.isfile(content):
                with open(content, "rb") as file:
                    content_data = file.read()
                    media_type, _ = mimetypes.guess_type(content)
                    return FastAPIResponse(content=content_data, media_type=media_type)
            elif content_type == ContentType.TEXT:
                return FastAPIResponse(content=content, media_type="text/plain")
        elif isinstance(content, bytes):
            return FastAPIResponse(
                content=content, media_type="application/octet-stream"
            )

    def save(self, content_type: ContentType, file_path: str):
        content = self.get_cleaned_content(content_type)

        if isinstance(content, (Image.Image, np.ndarray)):
            img = (
                content
                if isinstance(content, Image.Image)
                else Image.fromarray(content)
            )
            try:
                img.save(file_path)
            except Exception as e:
                if "unknown file extension" in str(e):
                    img.save(file_path, format=DEFAULT_IMAGE_FORMAT)
        else:
            with open(file_path, "wb") as file:
                if isinstance(content, str):
                    if content.startswith(("http://", "https://")):
                        response = requests.get(content)
                        file.write(response.content)
                    elif content.startswith("data:"):
                        header, encoded = content.split(",", 1)
                        content_data = base64.b64decode(encoded)
                        file.write(content_data)
                    elif os.path.isfile(content):
                        with open(content, "rb") as src_file:
                            file.write(src_file.read())
                    elif content_type == ContentType.TEXT:
                        file.write(content)
                elif isinstance(content, bytes):
                    file.write(content)

    def to_pil_image(
        self, content_type: ContentType = ContentType.IMAGE
    ) -> Image.Image:
        content = self.get_cleaned_content(content_type)

        if isinstance(content, Image.Image):
            return content
        elif isinstance(content, np.ndarray):
            return Image.fromarray(content)
        else:
            img = url_to_pil_image(content)
            if img is None:
                raise Exception("Invalid image URL. Please provide a valid image URL.")
            return img

    def to_cv2_image(self, content_type: ContentType = ContentType.IMAGE) -> np.ndarray:
        content = self.get_cleaned_content(content_type)

        if isinstance(content, np.ndarray):
            return content
        elif isinstance(content, Image.Image):
            return np.array(content)
        else:
            img = url_to_cv2_image(content)
            if img is None:
                raise Exception("Invalid image URL. Please provide a valid image URL.")
            return img

    def has_image(self) -> bool:
        return self.has_content(ContentType.IMAGE)

    def has_mask(self) -> bool:
        return self.has_content(ContentType.MASK)
