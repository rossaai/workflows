from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, root_validator
import random
from pydantic.fields import FieldInfo

from .constants import MAX_SAFE_DECIMAL, MAX_SAFE_INTEGER


class ControlType(str, Enum):
    CONTROL_REFERENCE = "control_reference"
    CONTROL_INPAINTING = "control_mask"
    CONTROL_UPSCALE = "control_upscale"
    CONTROL_FACE_DETAILER = "control_face_detailer"
    CONTROL_SEAMLESS_TILING = "control_seamless_tiling"
    CONTROL_LINE_ART = "control_lineart"
    CONTROL_CANNY = "control_canny"
    CONTROL_POSE = "control_pose"
    CONTROL_DEPTH = "control_depth"
    CONTROL_REGIONAL_PROMPT = "control_regional_prompt"
    CONTROL_STYLE_TRANSFER = "control_style_transfer"
    CONTROL_COMPOSITION_TRANSFER = "control_composition_transfer"
    CONTROL_FACE_REPLACEMENT = "control_face_replacement"
    CONTROL_RELIGHTING = "control_relight"
    CONTROL_TRY_ON = "control_try_on"
    CONTROL_OVERLAY = "control_overlay"
    CONTROL_EFFECT = "control_effect"
    CONTROL_TRANSPARENT_BACKGROUND = "control_transparent_background"
    CONTROL_EXPAND = "control_expand"
    CONTROL_REMOVE_OBJECT = "control_remove_object"


class ContentType(str, Enum):
    MASK = "mask"
    IMAGE = "image"
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
    COLOR = "color"

    # Similar
    CONTROLS = "controls"
    DYNAMIC_FORM = "dynamic_form"


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


class BaseModelWithAdvancedFields(BaseModel):
    advanced_fields: Optional[Dict[str, Any]] = None

    class Config:
        arbitrary_types_allowed = True

    def get_advanced_field(self, field_name: str, default: Any = None):
        """Gets an advanced field by name."""
        if self.advanced_fields is None:
            return default

        return self.advanced_fields.get(field_name, default)


class Option(BaseModel):
    value: str
    title: str
    description: Optional[str] = None
    advanced_fields: Optional[List[FieldInfo]] = None

    class Config:
        arbitrary_types_allowed = True

    @root_validator(pre=True)
    def validate_every_advanced_field_has_alias(cls, values):
        """Validates that every advanced field has an alias."""
        if "advanced_fields" in values and values["advanced_fields"] is not None:
            for field in values["advanced_fields"]:
                if not hasattr(field, "alias") or field.alias is None:
                    raise Exception(f"Advanced field {field} must have an alias.")

        return values


class OptionValue(BaseModelWithAdvancedFields):
    value: str
