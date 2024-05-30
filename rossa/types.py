import base64
from enum import Enum
import io
import mimetypes
import os
from typing import Dict, Optional, Union
from pydantic import BaseModel, Field
import requests
from fastapi import Response as FastAPIResponse
import random

from .image_conversion_utils import url_to_cv2_image, url_to_pil_image
from .constants import (
    DEFAULT_IMAGE_FORMAT,
    DEFAULT_IMAGE_MIME_TYPE,
    MAX_SAFE_DECIMAL,
    MAX_SAFE_INTEGER,
)
from PIL import Image
import numpy as np


class ControlType(str, Enum):
    INPUT = "input"
    MASK = "mask"
    CONTROL_UPSCALE = "control-upscale"
    CONTROL_FACE_DETAILER = "control-face-detailer"
    CONTROL_SEAMLESS_PATTERN = "control-seamless-pattern"
    CONTROL_LINE_ART = "control-lineart"
    CONTROL_CANNY = "control-canny"
    CONTROL_POSE = "control-pose"
    CONTROL_DEPTH = "control-depth"
    CONTROL_REGIONAL_PROMPT = "control-regional-prompt"
    CONTROL_STYLE_TRANSFER = "control-style-transfer"
    CONTROL_COMPOSITION_TRANSFER = "control-composition-transfer"
    CONTROL_FACE_REPLACEMENT = "control-face-replacement"
    CONTROL_RELIGHTING = "control-relight"
    CONTROL_TRANSPARENT_BACKGROUND = "control-transparent-background"


class ContentType(str, Enum):
    IMAGE = "image"
    MASK = "mask"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"
    THREE_D = "threed"


class ProgressNotificationType(str, Enum):
    PROGRESS = "progress"
    ERROR = "error"
    SUCCESS = "success"


class ApplicableElement(str, Enum):
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
    SLIDER = "slider"
    INTEGER = "integer"
    CHECKBOX = "checkbox"
    SELECT = "select"
    PROMPT = "prompt"
    NEGATIVE_PROMPT = "negative_prompt"
    PERFORMANCE = "performance"
    CONTROLS = "controls"


class FormatType(str, Enum):
    PERCENTAGE = "percentage"
    SCALE = "scale"
    DECIMAL = "decimal"
    INTEGER = "integer"


class GeneratorType(str, Enum):
    RANDOM_INTEGER = "random_integer"
    RANDOM_DECIMAL = "random_decimal"

    def generate(self, ge: Optional[float] = None, le: Optional[float] = None):
        if self == GeneratorType.RANDOM_INTEGER:
            return random.randint(ge or 0, le or MAX_SAFE_INTEGER)
        elif self == GeneratorType.RANDOM_DECIMAL:
            return random.randint(
                ge or 0.0, le or MAX_SAFE_DECIMAL
            )  # Adjust range as needed


class Option(BaseModel):
    value: str
    title: str
    description: Optional[str] = None
    default: Optional[bool] = False


class Content(BaseModel):
    contents: Dict[ContentType, Union[str, bytes, Image.Image, np.ndarray]] = Field(
        description="Dictionary mapping ContentType to content as str (URL, data URL-base64, or path), bytes, PIL Image, or NumPy array"
    )
    control_type: ControlType

    class Config:
        arbitrary_types_allowed = True

    def to_response(self, content_type: ContentType) -> FastAPIResponse:
        content = self.contents.get(content_type)
        if content is None:
            raise ValueError(f"No content found for content type: {content_type}")

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
        content = self.contents.get(content_type)
        if content is None:
            raise ValueError(f"No content found for content type: {content_type}")

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
        content = self.contents.get(content_type)
        if content is None:
            raise Exception(f"{content_type} content is not provided.")
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
        content = self.contents.get(content_type)
        if content is None:
            raise Exception(f"{content_type} content is not provided.")
        if isinstance(content, np.ndarray):
            return content
        elif isinstance(content, Image.Image):
            return np.array(content)
        else:
            img = url_to_cv2_image(content)
            if img is None:
                raise Exception("Invalid image URL. Please provide a valid image URL.")
            return img

    def has_mask(self) -> bool:
        return ContentType.MASK in self.contents
