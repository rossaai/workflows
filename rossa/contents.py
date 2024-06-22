import base64
import io
import mimetypes
import os
from typing import Any, Dict, Union, Optional
import requests
from fastapi import Response as FastAPIResponse

from .field_values import FieldValue
from .reserved_field_values import ReservedFieldValue

from pydantic import BaseModel, create_model, validator
from .types import ContentType
from .image_conversion_utils import url_to_cv2_image, url_to_pil_image
from .constants import (
    DEFAULT_IMAGE_FORMAT,
    DEFAULT_IMAGE_MIME_TYPE,
)
from PIL import Image
import numpy as np


class Content(BaseModel):
    type: ContentType
    content: Union[str, bytes, Image.Image, np.ndarray]
    settings: Dict[str, Any] = {}

    @validator("settings", pre=True)
    def validate_settings(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        SettingsModel = create_model(
            "SettingsModel",
            __root__=(
                Dict[str, Union[FieldValue, ReservedFieldValue]],
                ...,
            ),
        )

        SettingsModel(__root__=v)
        return v

    class Config:
        arbitrary_types_allowed = True

    def get_setting(self, key: str, default: Optional[Any] = None) -> Any:
        return self.settings.get(key, default)

    def to_response(self):
        content = self.content

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
            else:
                return FastAPIResponse(content=content, media_type="text/plain")
        elif isinstance(content, bytes):
            return FastAPIResponse(
                content=content, media_type="application/octet-stream"
            )

    def save(self, file_path: str):
        content = self.content

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
                    else:
                        file.write(content.encode("utf-8"))
                elif isinstance(content, bytes):
                    file.write(content)

    def to_pil_image(self) -> Image.Image:
        content = self.content

        if isinstance(content, Image.Image):
            return content
        elif isinstance(content, np.ndarray):
            return Image.fromarray(content)
        else:
            img = url_to_pil_image(content)
            if img is None:
                raise Exception("Invalid image URL. Please provide a valid image URL.")
            return img

    def to_cv2_image(self) -> np.ndarray:
        content = self.content

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
        return any(content.type == ContentType.IMAGE for content in self.contents)

    def has_mask(self) -> bool:
        return any(content.type == ContentType.MASK for content in self.contents)
