from typing import Optional, Union
from pydantic import BaseModel, Field
from fastapi import Response as FastAPIResponse
from .types import ContentType, ProgressNotificationType
from .contents import Content


class Response(Content):
    pass


class ImageResponse(Response):
    type: ContentType = ContentType.IMAGE


class VideoResponse(Response):
    type: ContentType = ContentType.VIDEO


class AudioResponse(Response):
    type: ContentType = ContentType.AUDIO


class ThreeDResponse(Response):
    type: ContentType = ContentType.THREE_D


class TextResponse(Response):
    type: ContentType = ContentType.TEXT


class Notification(BaseModel):
    type: ProgressNotificationType
    title: Optional[str] = Field(default=None, description="Optional progress title")
    progress: float = Field(ge=0, le=1, description="Progress value between 0 and 1")
    message: str = Field(default=None, description="Optional progress message")


class ProgressNotification(Notification):
    type: ProgressNotificationType = ProgressNotificationType.PROGRESS


class ErrorNotification(ProgressNotification):
    type: ProgressNotificationType = ProgressNotificationType.ERROR
    progress: float = Field(default=1.0)
    traceback: Optional[str] = Field(default=None, description="Optional traceback")


class SuccessNotification(ProgressNotification):
    type: ProgressNotificationType = ProgressNotificationType.SUCCESS
    progress: float = Field(default=1.0)
