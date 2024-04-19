import mimetypes
from typing import Optional, Union
from pydantic import BaseModel, Field
from PIL import Image
import numpy as np
import base64
import io
import os

import requests

from .types import ContentType


DEFAULT_IMAGE_FORMAT = "PNG"


class BaseResponse(BaseModel):
    content_type: ContentType

    class Config:
        arbitrary_types_allowed = True


class ImageResponse(BaseResponse):
    content_type: ContentType = ContentType.IMAGE
    content: Union[Image.Image, np.ndarray, str] = Field(
        description="Image content as PIL Image, Numpy array, path, URL or base64"
    )

    def save(self, file_path: str) -> None:
        if isinstance(self.content, Image.Image):
            self.content.save(file_path)
        elif isinstance(self.content, np.ndarray):
            Image.fromarray(self.content).save(file_path)
        elif isinstance(self.content, str) and self.content.startswith(
            ("http://", "https://")
        ):
            Image.open(io.BytesIO(requests.get(self.content).content)).save(file_path)
        elif isinstance(self.content, str) and self.content.startswith("content:"):
            header, encoded = self.content.split(",", 1)
            content = base64.b64decode(encoded)
            Image.open(io.BytesIO(content)).save(file_path)
        else:
            os.rename(self.content, file_path)

    def to_base64(self, format: str = DEFAULT_IMAGE_FORMAT) -> str:
        if isinstance(self.data, Image.Image):
            buffered = io.BytesIO()
            format = format or self.data.format or DEFAULT_IMAGE_FORMAT
            self.data.save(buffered, format=format)
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            mime_type = mimetypes.types_map.get(f".{format.lower()}", "image/png")
            return f"data:{mime_type};base64,{img_str}"
        elif isinstance(self.data, np.ndarray):
            img = Image.fromarray(self.data)
            buffered = io.BytesIO()
            format = format or DEFAULT_IMAGE_FORMAT
            img.save(buffered, format=format)
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            mime_type = mimetypes.types_map.get(f".{format.lower()}", "image/png")
            return f"data:{mime_type};base64,{img_str}"
        elif isinstance(self.data, str) and self.data.startswith(
            ("http://", "https://")
        ):
            return self.data
        elif isinstance(self.data, str) and self.data.startswith("data:"):
            return self.data
        else:
            mime_type, _ = mimetypes.guess_type(self.data)
            with open(self.data, "rb") as f:
                img_str = base64.b64encode(f.read()).decode("utf-8")
                return f"data:{mime_type};base64,{img_str}"


class VideoResponse(BaseResponse):
    content_type: ContentType = ContentType.VIDEO
    content: str = Field(description="Video content as path or URL")


class AudioResponse(BaseResponse):
    content_type: ContentType = ContentType.AUDIO
    content: str = Field(description="Audio content as path or URL")


class TextResponse(BaseResponse):
    content_type: ContentType = ContentType.TEXT
    content: str = Field(description="Text content")


class ThreeDResponse(BaseResponse):
    content_type: ContentType = ContentType.THREE_D
    content: str = Field(description="3D content as path or URL")


class ProgressNotification(BaseModel):
    progress: float = Field(ge=0, le=1, description="Progress value between 0 and 1")
    message: str = Field(default=None, description="Optional progress message")
    title: Optional[str] = Field(default=None, description="Optional progress title")


Response = Union[
    ImageResponse,
    VideoResponse,
    AudioResponse,
    TextResponse,
    ThreeDResponse,
]
