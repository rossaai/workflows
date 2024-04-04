from pydantic import BaseModel, Field as PydanticField
from typing import List, Optional, Union
from enum import Enum
from .utils import url_to_pil_image, url_to_cv2_image


class Option(BaseModel):
    value: str
    title: str
    description: Optional[str] = None
    tooltip: Optional[str] = None
    default: Optional[bool] = False


# CONTENT TYPE
class ContentType(Enum):
    IMAGE = "image"
    TEXT = "text"
    VIDEO = "video"
    THREE_D = "threed"
    AUDIO = "audio"


# CONTROLS
class ControlType(Enum):
    INPUT = "input"
    MASK = "mask"
    CONTROL_CANNY = "control-canny"
    CONTROL_POSE = "control-pose"
    CONTROL_IMAGE_PROMPT = "control-image-prompt"
    CONTROL_FACE_SWAP = "control-face-swap"


class ControlValue(BaseModel):
    type: Union[ControlType, str]
    influence: float
    url: str

    def to_pil_image(self):
        return url_to_pil_image(self.url)

    def to_cv2_image(self):
        return url_to_cv2_image(self.url)


class BaseControl(Option):
    value: Union[ControlType, str]


class InputControl(BaseControl):
    value: ControlType = ControlType.INPUT
    title: str = "Input"
    description: str = "Input for generation."
    tooltip: str = "Use text, images, or videos to guide generation."


class MaskControl(BaseControl):
    value: ControlType = ControlType.MASK
    title: str = "Mask"
    description: str = "Mask for generation."
    tooltip: str = "Use masks to guide generation."


class CannyControl(BaseControl):
    value: ControlType = ControlType.CONTROL_CANNY
    title: str = "Edges Control"
    description: str = "Detects edges useful sketch-to-render images."
    tooltip: str = "Enhances edge detection in high-res images."


class PoseControl(BaseControl):
    value: ControlType = ControlType.CONTROL_POSE
    title: str = "Pose"
    description: str = "Incorporates a specific pose into your image generation."
    tooltip: str = "Incorporate poses into new images."


# class ImagePromptControl(BaseControl):
#     value: ControlType = ControlType.CONTROL_IMAGE_PROMPT
#     title: str = "Image Prompt"
#     description: str = "Use an image to guide style, composition, and colors."
#     tooltip: str = "Combine images and text for nuanced results."


# class FaceSwapControl(BaseControl):
#     value: ControlType = ControlType.CONTROL_FACE_SWAP
#     title: str = "Face Swap"
#     description: str = "Incorporates a specific face into your image generation."
#     tooltip: str = "Incorporate facial features into new images."


# PERFORMANCE
class PerformanceType(Enum):
    INSTANT = "instant"
    BALANCED = "balanced"
    QUALITY = "quality"


class BasePerformance(Option):
    value: PerformanceType


class InstantPerformance(BasePerformance):
    value: PerformanceType = PerformanceType.INSTANT
    title: str = "Instant"
    description: str = "Real-time generation (up to 2 seconds)."
    tooltip: str = "Extreme speed, instant results."
    default: bool = False


class BalancedPerformance(BasePerformance):
    value: PerformanceType = PerformanceType.BALANCED
    title: str = "Balanced"
    description: str = "Efficient speed and quality balance (up to 10 seconds)."
    tooltip: str = "Ideal balance between speed and quality."
    default: bool = True


class QualityPerformance(BasePerformance):
    value: PerformanceType = PerformanceType.QUALITY
    title: str = "Quality"
    description: str = "Maximum quality (up to 20 seconds)."
    tooltip: str = "For when quality is everything."
    default: bool = False


# FIELDS
def TextField(
    title: str,
    description: str,
    placeholder: str = "",
    **kwargs,
):
    return PydanticField(
        title=title,
        description=description,
        placeholder=placeholder,
        type="text",
        **kwargs,
    )


def TextAreaField(
    title: str,
    description: str,
    placeholder: str = "",
    **kwargs,
):
    return PydanticField(
        title=title,
        description=description,
        placeholder=placeholder,
        type="textarea",
        **kwargs,
    )


def NumberField(
    title: str,
    description: str,
    placeholder: str = "",
    min: Optional[float] = None,
    max: Optional[float] = None,
    step: Optional[float] = None,
    **kwargs,
):
    return PydanticField(
        title=title,
        description=description,
        placeholder=placeholder,
        type="number",
        ge=min,
        le=max,
        step=step,
        **kwargs,
    )


def IntegerField(
    title: str,
    description: str,
    placeholder: str = "",
    min: Optional[int] = None,
    max: Optional[int] = None,
    step: Optional[int] = None,
    **kwargs,
):
    return PydanticField(
        title=title,
        description=description,
        placeholder=placeholder,
        type="integer",
        ge=min,
        le=max,
        step=step,
        **kwargs,
    )


def CheckboxField(
    title: str,
    description: str,
    placeholder: str = "",
    **kwargs,
):
    return PydanticField(
        title=title,
        description=description,
        placeholder=placeholder,
        type="checkbox",
        default=False,
        **kwargs,
    )


def SelectField(
    title: str,
    description: str,
    options: List[Option],
    placeholder: str = "",
    **kwargs,
):
    return PydanticField(
        title=title,
        description=description,
        placeholder=placeholder,
        type="select",
        options=options,
        default=[],
        **kwargs,
    )


# RESERVED FIELDS
def PromptField(
    title: str = "Prompt",
    description: str = "Prompt for the model.",
    placeholder: str = "What do you want to create?",
    **kwargs,
):
    return PydanticField(
        alias="prompt",
        title=title,
        description=description,
        placeholder=placeholder,
        type="textarea",
        default="",
        **kwargs,
    )


def NegativePromptField(
    title: str = "Negative Prompt",
    description: str = "Negative prompt for the model.",
    placeholder: str = "What do you want to avoid?",
    **kwargs,
):
    return PydanticField(
        alias="negative_prompt",
        title=title,
        description=description,
        placeholder=placeholder,
        type="textarea",
        default="",
        **kwargs,
    )


def PerformanceField(
    title: str = "Performance",
    description: str = "Performance settings.",
    options: List[BasePerformance] = [],
    **kwargs,
):
    return PydanticField(
        alias="performance",
        default=[],
        title=title,
        description=description,
        options=options,
        **kwargs,
    )


def ControlsField(
    title: str = "Controls",
    description: str = "List of controls.",
    options: List[BaseControl] = [],
    **kwargs,
):
    return PydanticField(
        alias="controls",
        default=[],
        title=title,
        description=description,
        options=options,
        **kwargs,
    )


def ModelField(
    title: str = "Model",
    description: str = "Model settings.",
    **kwargs,
):
    return PydanticField(
        title=title,
        description=description,
        default=None,
        **kwargs,
    )
