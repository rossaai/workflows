import base64
from enum import Enum
import mimetypes
import os
from typing import Optional, Union
from pydantic import BaseModel, Field
import requests
from fastapi import Response as FastAPIResponse


class ControlType(str, Enum):
    INPUT = "input"
    MASK = "mask"
    CONTROL_CANNY = "control-canny"
    CONTROL_POSE = "control-pose"
    CONTROL_LINE_ART = "control-lineart"
    CONTROL_STYLE_TRANSFER = "control-style-transfer"
    CONTROL_COMPOSITION_TRANSFER = "control-composition-transfer"
    CONTROL_FACE_REPLACEMENT = "control-face-replacement"


class ContentType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"
    THREE_D = "threed"


class ProgressNotificationType(str, Enum):
    PROGRESS = "progress"
    ERROR = "error"
    SUCCESS = "success"


class ApplicableFor(str, Enum):
    """
    An enumeration representing the applicability of a requirement.

    Attributes:
        ALL (str): The requirement is applicable for both parent and child requirements.
        PARENT (str): The requirement is applicable for parent elements.
                      Parent elements are frame elements or playground page that control the generation.
        CHILD (str): The requirement is applicable for child elements.
                     Child elements are the elements inside the parent, almost always frame children.

    Examples:
        >>> requirement_applicability = ApplicableFor.ALL
        >>> print(requirement_applicability)
        all

        >>> if requirement_applicability == ApplicableFor.PARENT:
        ...     print("Requirement is applicable for parent elements.")
        ...
        Requirement is applicable for parent elements.
    """

    ALL = "all"
    PARENT = "parent"
    CHILD = "child"


class PerformanceType(str, Enum):
    INSTANT = "instant"
    BALANCED = "balanced"
    QUALITY = "quality"


class FieldType(str, Enum):
    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"
    INTEGER = "integer"
    CHECKBOX = "checkbox"
    SELECT = "select"
    PROMPT = "prompt"
    NEGATIVE_PROMPT = "negative_prompt"
    PERFORMANCE = "performance"
    CONTROLS = "controls"


class Option(BaseModel):
    value: str
    title: str
    description: Optional[str] = None
    default: Optional[bool] = False


class Content(BaseModel):
    content_type: Union[ContentType, str]
    control_type: ControlType = Field(description="Optional control type")
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
                content=self.content, media_type="application/octet-stream"
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
                    # file_name, file_extension = os.path.splitext(file_path)

                    # header, encoded = self.content.split(",", 1)
                    # content = base64.b64decode(encoded)

                    # # Extract the MIME type from the header
                    # mime_type = header.split(":")[1].split(";")[0]

                    # # Get the file extension based on the MIME type
                    # extension = mimetypes.guess_extension(mime_type)

                    # if extension and extension != file_extension:
                    #     # Create a new file path with the correct extension
                    #     new_file_path = file_name + extension

                    #     # Save the content to the new file path
                    #     with open(new_file_path, "wb") as new_file:
                    #         new_file.write(content)
                    # else:
                    #     # Save the content to the original file path
                    #     file.write(content)
                else:
                    with open(self.content, "rb") as src_file:
                        file.write(src_file.read())
            elif isinstance(self.content, bytes):
                file.write(self.content)
