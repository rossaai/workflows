from typing import Optional, Union
from pydantic import BaseModel, Field
from PIL import Image
import numpy as np
import io
from fastapi import Response as FastAPIResponse
from .types import Content, ContentType, ControlType, ProgressNotificationType


DEFAULT_IMAGE_FORMAT = "PNG"
DEFAULT_IMAGE_MIME_TYPE = "image/png"


class BaseResponse(Content):
    control_type: ControlType = Field(
        default=ControlType.INPUT, description="Optional control type"
    )


class ImageResponse(BaseResponse):
    content_type: ContentType = ContentType.IMAGE
    content: Union[Image.Image, np.ndarray, str, bytes] = Field(
        description="Image content as PIL Image, Numpy array, str (URL, data URL-base64, or path), or bytes"
    )

    def to_response(self) -> FastAPIResponse:
        if isinstance(self.content, (Image.Image, np.ndarray)):
            buffered = io.BytesIO()
            if isinstance(self.content, Image.Image):
                self.content.save(buffered, format=DEFAULT_IMAGE_FORMAT)
            else:
                Image.fromarray(self.content).save(
                    buffered, format=DEFAULT_IMAGE_FORMAT
                )
            content = buffered.getvalue()
            return FastAPIResponse(content=content, media_type=DEFAULT_IMAGE_MIME_TYPE)
        else:
            return super().to_response()

    def save(self, file_path: str):
        if isinstance(self.content, (Image.Image, np.ndarray)):
            img = None

            if isinstance(self.content, Image.Image):
                img = self.content
            else:
                img = Image.fromarray(self.content)

            try:
                img.save(file_path)
            except Exception as e:
                if "unknown file extension" in str(e):
                    img.save(file_path, format=DEFAULT_IMAGE_FORMAT)
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
