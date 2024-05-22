from typing import Optional, Union
from pydantic import BaseModel, Field
from fastapi import Response as FastAPIResponse
from .types import Content, ContentType, ControlType, ProgressNotificationType
from PIL import Image
import numpy as np


class BaseResponse(Content):
    pass


class BaseTextResponse(BaseResponse):
    def to_response(self) -> FastAPIResponse:
        content = self.contents.get(ContentType.TEXT)
        return FastAPIResponse(content=content, media_type="text/plain")

    def save(self, file_path: str):
        content = self.contents.get(ContentType.TEXT)
        with open(file_path, "w") as file:
            file.write(content)


def ImageResponse(
    content: Union[str, bytes, Image.Image, np.ndarray],
    control_type: Optional[ControlType] = None,
):
    return BaseResponse(
        contents={ContentType.IMAGE: content},
        control_type=control_type,
    )


def VideoResponse(
    content: Union[str, bytes],
    control_type: Optional[ControlType] = None,
):
    return BaseResponse(
        contents={ContentType.VIDEO: content},
        control_type=control_type,
    )


def AudioResponse(
    content: Union[str, bytes],
    control_type: Optional[ControlType] = None,
):
    return BaseResponse(
        contents={ContentType.AUDIO: content},
        control_type=control_type,
    )


def ThreeDResponse(
    content: Union[str, bytes],
    control_type: Optional[ControlType] = None,
):
    return BaseResponse(
        contents={ContentType.THREE_D: content},
        control_type=control_type,
    )


def TextResponse(
    content: str,
    control_type: Optional[ControlType] = None,
):
    return BaseTextResponse(
        contents={ContentType.TEXT: content},
        control_type=control_type,
    )


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
