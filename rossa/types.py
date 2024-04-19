from enum import Enum


class ContentType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"
    THREE_D = "threed"
