from enum import Enum


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
