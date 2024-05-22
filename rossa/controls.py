from pydantic import BaseModel, Field as PydanticField, root_validator
from typing import Any, Dict, List, Optional, Union

from .types import Content, Option, ContentType, ControlType
from .fields import BaseFieldInfo


class ControlValue(Content):
    influence: float
    advanced_fields: Optional[Dict[str, Any]] = None

    def get_advanced_field(self, field_name: str, default: Any = None):
        """Gets an advanced field by name."""
        if self.advanced_fields is None:
            return default

        return self.advanced_fields.get(field_name, default)


class ControlContent(BaseModel):
    content_type: ContentType
    is_required: bool = True


class ImageControlContent(ControlContent):
    content_type: ContentType = ContentType.IMAGE


class MaskControlContent(ControlContent):
    content_type: ContentType = ContentType.MASK


class VideoControlContent(ControlContent):
    content_type: ContentType = ContentType.VIDEO


class AudioControlContent(ControlContent):
    content_type: ContentType = ContentType.AUDIO


class TextControlContent(ControlContent):
    content_type: ContentType = ContentType.TEXT


class ThreeDControlContent(ControlContent):
    content_type: ContentType = ContentType.THREE_D


class BaseControl(Option):
    """
    Represents a control option with specific requirements and applicability.

    Attributes:
        value (Union[ControlType, str]): The value of the control option.
        content_type (ContentType): The type of content the control option applies to.
        applicable_elements (List[ApplicableElement]): The elements to which the control option is applicable.
        requirements (Optional[ApplicabilityControlRequirements]): The requirements for the control option's applicability.
        advanced_fields (Optional[List[AdvancedField]]): Additional advanced fields for the control option.
    """

    value: Union[ControlType, str]
    content_type: ContentType
    supported_contents: List[ControlContent]
    advanced_fields: Optional[List[BaseFieldInfo]] = None

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

    @root_validator(pre=True)
    def validate_supported_contents(cls, values):
        """Validates that the supported contents are valid."""
        if "supported_contents" in values and values["supported_contents"] is not None:
            for content in values["supported_contents"]:
                if not isinstance(content, ControlContent):
                    raise Exception(
                        f"Supported content {content} must be a ControlContent."
                    )

            if len(values["supported_contents"]) == 0:
                raise Exception("Supported contents cannot be empty.")

        return values


class InputControl(BaseControl):
    value: ControlType = ControlType.INPUT
    title: str = "Source"
    description: str = "Input for generation."


class MaskControl(BaseControl):
    value: ControlType = ControlType.MASK
    title: str = "Mask"
    description: str = "Mask for generation."


class CannyControl(BaseControl):
    value: ControlType = ControlType.CONTROL_CANNY
    title: str = "Edges Control"
    description: str = "Detects edges useful sketch-to-render images."


class LineArtControl(BaseControl):
    value: ControlType = ControlType.CONTROL_LINE_ART
    title: str = "Line Art"
    description: str = (
        "Incorporates line art into your generation. Useful for sketch-to-image tasks."
    )


class PoseControl(BaseControl):
    value: ControlType = ControlType.CONTROL_POSE
    title: str = "Pose Guide"
    description: str = "Incorporates a specific pose into your generation."


class DepthControl(BaseControl):
    value: ControlType = ControlType.CONTROL_DEPTH
    title: str = "Depth"
    description: str = "Incorporates depth into your generation."


class StyleTransferControl(BaseControl):
    value: ControlType = ControlType.CONTROL_STYLE_TRANSFER
    title: str = "Style Transfer"
    description: str = "Incorporates style into your generation."


class FaceReplacementControl(BaseControl):
    value: ControlType = ControlType.CONTROL_FACE_REPLACEMENT
    title: str = "Face Replacement"
    description: str = "Replaces faces in your generation."


class TransparentBackgroundControl(BaseControl):
    value: ControlType = ControlType.CONTROL_TRANSPARENT_BACKGROUND
    title: str = "Transparent Background"
    description: str = "When generating it keeps the background transparent"


# IMAGE CONTROLS
class InputImageControl(InputControl):
    title: str = "Source Image"
    description: str = "Provide an input image for Image generation."
    content_type: ContentType = ContentType.IMAGE
    supported_contents: List[ControlContent] = [ImageControlContent()]


class MaskImageControl(MaskControl):
    title: str = "Mask"
    description: str = "Define areas to be modified for Image generation."
    content_type: ContentType = ContentType.IMAGE
    supported_contents: List[ControlContent] = [MaskControlContent()]


class CannyImageControl(CannyControl):
    title: str = "Edge Detection"
    description: str = "Emphasize edges for sketch-to-image generation."
    content_type: ContentType = ContentType.IMAGE
    supported_contents: List[ControlContent] = [ImageControlContent()]


class LineArtImageControl(LineArtControl):
    title: str = "Line Art Guide"
    description: str = (
        "Emphasize lines for constraining the generated image. Very useful for sketch-to-image generation."
    )
    content_type: ContentType = ContentType.IMAGE
    supported_contents: List[ControlContent] = [ImageControlContent()]


class PoseImageControl(PoseControl):
    title: str = "Pose Guide"
    description: str = (
        "Specify a pose to be incorporated into the generated image. Useful for complex poses."
    )
    content_type: ContentType = ContentType.IMAGE
    supported_contents: List[ControlContent] = [ImageControlContent()]


class DepthImageControl(DepthControl):
    title: str = "Depth Guide"
    description: str = (
        "Incorporate depth into the generated image. Useful for 3D effects."
    )
    content_type: ContentType = ContentType.IMAGE
    supported_contents: List[ControlContent] = [ImageControlContent()]


class StyleTransferImageControl(StyleTransferControl):
    title: str = "Style Transfer"
    description: str = (
        "Use an image to influence the style, composition, and colors of the generated result."
    )
    content_type: ContentType = ContentType.IMAGE
    supported_contents: List[ControlContent] = [ImageControlContent()]


class FaceReplacementImageControl(FaceReplacementControl):
    title: str = "Face Transfer"
    description: str = (
        "Incorporate a face into the generated image. Useful for portraits or character design."
    )
    content_type: ContentType = ContentType.IMAGE
    supported_contents: List[ControlContent] = [ImageControlContent()]


class TransparentBackgroundImageControl(TransparentBackgroundControl):
    title: str = "Transparent Background"
    description: str = "When generating it keeps the background transparent"
    content_type: ContentType = ContentType.IMAGE
    supported_contents: List[ControlContent] = [ImageControlContent()]
