from enum import Enum
import mimetypes
import os
from typing import Optional, Union
from pydantic import BaseModel, Field
from PIL import Image
import numpy as np
import base64
import io

import requests
from fastapi import Response as FastAPIResponse

from .types import ContentType, ProgressNotificationType


class BaseResponse(BaseModel):
    content_type: ContentType
    content: Union[str, bytes] = Field(
        description="Content as str (URL, data URL-base64, or path) or bytes"
    )

    class Config:
        arbitrary_types_allowed = True

    def to_response(self) -> FastAPIResponse:
        if isinstance(self.content, str):
            if self.content.startswith(("http://", "https://")):
                response = requests.get(self.content)
                return FastAPIResponse(
                    content=response.content,
                    media_type=response.headers["Content-Type"],
                )
            elif self.content.startswith("data:"):
                header, encoded = self.content.split(",", 1)
                media_type = header.split(":")[1].split(";")[0]
                content = base64.b64decode(encoded)
                return FastAPIResponse(content=content, media_type=media_type)
            else:
                if os.path.isfile(self.content):
                    with open(self.content, "rb") as file:
                        content = file.read()
                        media_type, _ = mimetypes.guess_type(self.content)
                        return FastAPIResponse(content=content, media_type=media_type)
                else:
                    raise ValueError(f"File not found: {self.content}")
        elif isinstance(self.content, bytes):
            return FastAPIResponse(
                content=self.content, media_type=self.content_type.value
            )

    def save(self, file_path: str):
        with open(file_path, "wb") as file:
            if isinstance(self.content, str):
                if self.content.startswith(("http://", "https://")):
                    response = requests.get(self.content)
                    file.write(response.content)
                elif self.content.startswith("data:"):
                    header, encoded = self.content.split(",", 1)
                    content = base64.b64decode(encoded)
                    file.write(content)
                else:
                    with open(self.content, "rb") as src_file:
                        file.write(src_file.read())
            elif isinstance(self.content, bytes):
                file.write(self.content)


class ImageResponse(BaseResponse):
    content_type: ContentType = ContentType.IMAGE
    content: Union[Image.Image, np.ndarray, str, bytes] = Field(
        description="Image content as PIL Image, Numpy array, str (URL, data URL-base64, or path), or bytes"
    )

    def to_response(self) -> FastAPIResponse:
        if isinstance(self.content, (Image.Image, np.ndarray)):
            buffered = io.BytesIO()
            if isinstance(self.content, Image.Image):
                self.content.save(buffered, format="PNG")
            else:
                Image.fromarray(self.content).save(buffered, format="PNG")
            content = buffered.getvalue()
            return FastAPIResponse(content=content, media_type=self.content_type.value)
        else:
            return super().to_response()

    def save(self, file_path: str):
        if isinstance(self.content, (Image.Image, np.ndarray)):
            if isinstance(self.content, Image.Image):
                self.content.save(file_path)
            else:
                Image.fromarray(self.content).save(file_path)
        else:
            super().save(file_path)


class VideoResponse(BaseResponse):
    content_type: ContentType = ContentType.VIDEO


class AudioResponse(BaseResponse):
    content_type: ContentType = ContentType.AUDIO


class TextResponse(BaseResponse):
    content_type: ContentType = ContentType.TEXT
    content: str = Field(description="Text content as string")

    def to_response(self) -> FastAPIResponse:
        return FastAPIResponse(content=self.content, media_type="text/plain")

    def save(self, file_path: str):
        with open(file_path, "w") as file:
            file.write(self.content)


class ThreeDResponse(BaseResponse):
    content_type: ContentType = ContentType.THREE_D


class BaseNotification(BaseModel):
    type: ProgressNotificationType
    progress: float = Field(ge=0, le=1, description="Progress value between 0 and 1")
    message: str = Field(default=None, description="Optional progress message")
    title: Optional[str] = Field(default=None, description="Optional progress title")


class ProgressNotification(BaseNotification):
    type: ProgressNotificationType = ProgressNotificationType.PROGRESS


class ErrorNotification(ProgressNotification):
    type: ProgressNotificationType = ProgressNotificationType.ERROR
    progress: float = Field(default=1.0)
    traceback: Optional[str] = Field(default=None, description="Optional traceback")


class SuccessNotification(ProgressNotification):
    type: ProgressNotificationType = ProgressNotificationType.SUCCESS
    progress: float = Field(default=1.0)


Response = Union[
    BaseResponse,
    ImageResponse,
    VideoResponse,
    AudioResponse,
    TextResponse,
    ThreeDResponse,
]


Notification = Union[ProgressNotification, ErrorNotification, SuccessNotification]
