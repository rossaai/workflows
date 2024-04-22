from enum import Enum


class ControlType(str, Enum):
    INPUT = "input"
    MASK = "mask"
    CONTROL_CANNY = "control-canny"
    CONTROL_POSE = "control-pose"
    CONTROL_STYLE_TRANSFER = "control-style-transfer"
    CONTROL_FACE_SWAP = "control-face-swap"


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
