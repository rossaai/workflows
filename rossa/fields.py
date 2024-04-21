from pydantic import BaseModel, Field as PydanticField
from typing import List, Literal, Optional, Union
from enum import Enum

from .types import ApplicableFor
from .utils import url_to_pil_image, url_to_cv2_image


class Option(BaseModel):
    value: str
    title: str
    description: Optional[str] = None
    tooltip: Optional[str] = None
    default: Optional[bool] = False


# CONTROLS
class ControlType(str, Enum):
    INPUT = "input"
    MASK = "mask"
    CONTROL_CANNY = "control-canny"
    CONTROL_POSE = "control-pose"
    CONTROL_STYLE_TRANSFER = "control-style-transfer"
    CONTROL_FACE_SWAP = "control-face-swap"


class ControlValue(BaseModel):
    type: Union[ControlType, str]
    influence: float
    url: str

    def to_pil_image(self):
        """Converts a URL to a PIL image."""
        img = url_to_pil_image(self.url)

        if img is None:
            raise Exception("Invalid image URL. Please provide a valid image URL.")

        return img

    def to_cv2_image(self):
        "" 'Converts a URL to a cv2 image. Remember to `.apt_install("ffmpeg", "libsm6", "libxext6")` to your `rossa.Image`.' ""
        img = url_to_cv2_image(self.url)

        if img is None:
            raise Exception("Invalid image URL. Please provide a valid image URL.")

        return img


class ApplicableForRequeriments(BaseModel):
    """
    Represents the requirements for a specific applicability level.

    Attributes:
        required (bool): Indicates whether the requirement is mandatory. Default is False.
        editable (bool): Indicates whether the requirement is editable. Default is True.

    Examples:
        >>> reqs = ApplicableForRequeriments(required=True, editable=False)
        >>> print(reqs.required)
        True
        >>> print(reqs.editable)
        False
    """

    required: bool = False
    editable: bool = True


class ControlRequeriments(BaseModel):
    """
    Represents the control requirements for different applicability levels.

    Attributes:
        all (Optional[ApplicableForRequeriments]): The requirements applicable for all levels.
        parent (Optional[ApplicableForRequeriments]): The requirements applicable for the parent level.
        child (Optional[ApplicableForRequeriments]): The requirements applicable for the child level.

    Examples:
        >>> control_reqs = ControlRequeriments(
        ...     all=ApplicableForRequeriments(required=True),
        ...     parent=ApplicableForRequeriments(editable=False),
        ...     child=ApplicableForRequeriments(required=False, editable=True)
        ... )
        >>> print(control_reqs.all.required)
        True
        >>> print(control_reqs.parent.editable)
        False
        >>> print(control_reqs.child.required)
        False
    """

    all: Optional[ApplicableForRequeriments]
    parent: Optional[ApplicableForRequeriments]
    child: Optional[ApplicableForRequeriments]


class BaseControl(Option):
    value: Union[ControlType, str]
    applicable_for: List[ApplicableFor] = PydanticField(
        default=[ApplicableFor.ALL],
        title="Applicable For",
        description="The control is applicable for the following elements.",
    )
    requeriments: Optional[ControlRequeriments]


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


class InputImageControl(InputControl):
    title: str = "Input Image"
    description: str = "Input image for generation."
    tooltip: str = "Use images to guide generation."
    applicable_for: List[ApplicableFor] = [ApplicableFor.PARENT]
    requeriments: ControlRequeriments = ControlRequeriments(
        all=ApplicableForRequeriments(editable=False),
        parent=ApplicableForRequeriments(required=True),
    )


class MaskImageControl(MaskControl):
    title: str = "Mask Image"
    description: str = "Mask image for generation."
    tooltip: str = "Use images as masks to guide generation."
    applicable_for: List[ApplicableFor] = [ApplicableFor.PARENT]
    requeriments: ControlRequeriments = ControlRequeriments(
        all=ApplicableForRequeriments(editable=False),
        parent=ApplicableForRequeriments(required=True),
    )


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
class PerformanceType(str, Enum):
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


FieldTypeLiteral = Literal[
    "text",
    "textarea",
    "number",
    "integer",
    "checkbox",
    "select",
    "prompt",
    "negative_prompt",
    "performance",
    "controls",
]


def BaseField(
    title: str,
    type: FieldTypeLiteral,
    description: str,
    alias: str = None,
    placeholder: str = "",
    options: Optional[List[Option]] = None,
    **kwargs,
):
    if options:
        for option in options:
            if not isinstance(option, Option):
                raise Exception("Field options must be a list of Option.")

    if type == FieldType.SELECT and not options:
        raise Exception("Select fields must have options.")

    if type == FieldType.PERFORMANCE and not options:
        raise Exception("Performance fields must have options.")

    if type == FieldType.CONTROLS and not options:
        raise Exception("Controls fields must have options.")

    # validate if type is in FieldType
    if type not in set(FieldType):
        raise Exception("Field type must be in FieldType.")

    return PydanticField(
        title=title,
        type=type,
        alias=alias,
        description=description,
        placeholder=placeholder,
        options=options,
        **kwargs,
    )


def TextField(
    title: str,
    description: str,
    placeholder: str = "",
    **kwargs,
):
    return BaseField(
        type=FieldType.TEXT.value,
        title=title,
        description=description,
        placeholder=placeholder,
        **kwargs,
    )


def TextAreaField(
    title: str,
    description: str,
    placeholder: str = "",
    **kwargs,
):
    return BaseField(
        type=FieldType.TEXTAREA.value,
        title=title,
        description=description,
        placeholder=placeholder,
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
    return BaseField(
        type=FieldType.NUMBER.value,
        title=title,
        description=description,
        placeholder=placeholder,
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
    return BaseField(
        type=FieldType.INTEGER.value,
        title=title,
        description=description,
        placeholder=placeholder,
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
    return BaseField(
        type=FieldType.CHECKBOX.value,
        title=title,
        description=description,
        placeholder=placeholder,
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
    return BaseField(
        type=FieldType.SELECT.value,
        title=title,
        description=description,
        placeholder=placeholder,
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
    return BaseField(
        type=FieldType.PROMPT.value,
        alias="prompt",
        title=title,
        description=description,
        placeholder=placeholder,
        default="",
        **kwargs,
    )


def NegativePromptField(
    title: str = "Negative Prompt",
    description: str = "Negative prompt for the model.",
    placeholder: str = "What do you want to avoid?",
    **kwargs,
):
    return BaseField(
        type=FieldType.NEGATIVE_PROMPT.value,
        alias="negative_prompt",
        title=title,
        description=description,
        placeholder=placeholder,
        default="",
        **kwargs,
    )


def PerformanceField(
    title: str = "Performance",
    description: str = "Performance settings.",
    options: List[BasePerformance] = [],
    **kwargs,
):
    for option in options:
        if not isinstance(option, BasePerformance):
            raise Exception("Performance options must be a list of BasePerformance.")

    return BaseField(
        type=FieldType.PERFORMANCE.value,
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
    for option in options:
        if not isinstance(option, BaseControl):
            raise Exception("Control options must be a list of BaseControl.")

    return BaseField(
        type=FieldType.CONTROLS.value,
        alias="controls",
        default=[],
        title=title,
        description=description,
        options=options,
        **kwargs,
    )