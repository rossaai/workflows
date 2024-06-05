import os
from pydantic import BaseModel, root_validator, Field as PydanticField
from typing import Any, Dict, List, Optional, Union

from .constants import REGIONAL_PROMPT_ADVANCED_FIELD_ALIAS

from .types import Content, Option, ContentType, ControlType
from .fields import BaseFieldInfo, TextAreaField


class ControlValue(Content):
    influence: float = PydanticField(
        title="Influence",
        description="The influence of the control value on the generation process.",
    )
    advanced_fields: Optional[Dict[str, Any]] = None

    def get_advanced_field(self, field_name: str, default: Any = None):
        """Gets an advanced field by name."""
        if self.advanced_fields is None:
            return default

        return self.advanced_fields.get(field_name, default)

    def is_prompt(self, content_type: ContentType = ContentType.MASK) -> bool:
        """Identify if the mask is a prompt."""

        content = self.get_content(content_type)

        return (
            isinstance(content, str)
            and not content.startswith(("http://", "https://", "data:"))
            and not os.path.isfile(content)
        )


class ControlContent(BaseModel):
    content_type: ContentType
    is_required: bool = True


class ImageControlContent(ControlContent):
    content_type: ContentType = ContentType.IMAGE


class VideoControlContent(ControlContent):
    content_type: ContentType = ContentType.VIDEO


class AudioControlContent(ControlContent):
    content_type: ContentType = ContentType.AUDIO


class TextControlContent(ControlContent):
    content_type: ContentType = ContentType.TEXT


class ThreeDControlContent(ControlContent):
    content_type: ContentType = ContentType.THREE_D


class MaskControlContent(ControlContent):
    content_type: ContentType = ContentType.MASK


class MaskFromPromptControlContent(ControlContent):
    content_type: ContentType = ContentType.MASK_FROM_PROMPT


class MaskFromColorControlContent(ControlContent):
    content_type: ContentType = ContentType.MASK_FROM_COLOR


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


class ReferenceControl(BaseControl):
    value: ControlType = ControlType.CONTROL_REFERENCE
    title: str = "Source"
    description: str = "Input for generation."


class InpaintingControl(BaseControl):
    value: ControlType = ControlType.CONTROL_INPAINTING
    title: str = "Inpainting"
    description: str = "Inpainting for generation."


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


class RegionalPromptControl(BaseControl):
    value: ControlType = ControlType.CONTROL_REGIONAL_PROMPT
    title: str = "Regional Prompt"
    description: str = "Incorporates regional prompt into your generation."
    advanced_fields: List[BaseFieldInfo] = [
        TextAreaField(
            alias=REGIONAL_PROMPT_ADVANCED_FIELD_ALIAS,
            title="Regional Prompt",
            description="Enter the regional prompt for the selected mask area.",
            placeholder="Write the regional prompt here.",
        ),
    ]


class UpscaleControl(BaseControl):
    value: ControlType = ControlType.CONTROL_UPSCALE
    title: str = "Upscale"
    description: str = "Upscale the generated image."


class FaceDetailerControl(BaseControl):
    value: ControlType = ControlType.CONTROL_FACE_DETAILER
    title: str = "Face Detailer"
    description: str = "Enhance the details of the face in the generated image."


class SeamlessTilingControl(BaseControl):
    value: ControlType = ControlType.CONTROL_SEAMLESS_TILING
    title: str = "Seamless Tiling"
    description: str = "Generate a seamless tailing from the input image."


class RelightingControl(BaseControl):
    value: ControlType = ControlType.CONTROL_RELIGHTING
    title: str = "Relighting"
    description: str = (
        "Change the illumination or weather conditions of the generated scene."
    )


class TryOnControl(BaseControl):
    value: ControlType = ControlType.CONTROL_TRY_ON
    title: str = "Try On"
    description: str = "Try On the clothes on the person in the image."


# IMAGE CONTROLSc
class ReferenceImageControl(ReferenceControl):
    title: str = "Reference"
    description: str = (
        "Guides the image generation process. Lower values blend the colors more, while higher values reduce the influence of the reference image."
    )
    content_type: ContentType = ContentType.IMAGE
    supported_contents: List[ControlContent] = [ImageControlContent()]


class InpaintingImageControl(InpaintingControl):
    title: str = "Inpainting"
    description: str = "Defines areas to be modified in the generated image."
    content_type: ContentType = ContentType.IMAGE
    supported_contents: List[ControlContent] = [
        ImageControlContent(is_required=False),
        MaskControlContent(),
    ]


class CannyImageControl(CannyControl):
    title: str = "Canny Edge Detection"
    description: str = "Emphasizes edges for sketch-to-image generation."
    content_type: ContentType = ContentType.IMAGE
    supported_contents: List[ControlContent] = [ImageControlContent()]


class LineArtImageControl(LineArtControl):
    title: str = "Line Guide"
    description: str = (
        "Extracts and guides the generation based on the contours and fine details of the provided image, without considering colors or other elements. Useful for sketch-to-image generation and line-based guidance."
    )
    content_type: ContentType = ContentType.IMAGE
    supported_contents: List[ControlContent] = [ImageControlContent()]


class PoseImageControl(PoseControl):
    title: str = "Pose Guide"
    description: str = (
        "Incorporates a specified pose into the generated image. Useful for complex poses."
    )
    content_type: ContentType = ContentType.IMAGE
    supported_contents: List[ControlContent] = [ImageControlContent()]


class DepthImageControl(DepthControl):
    title: str = "Depth Guide"
    description: str = (
        "Incorporates depth information into the generated image. Useful for 3D effects."
    )
    content_type: ContentType = ContentType.IMAGE
    supported_contents: List[ControlContent] = [ImageControlContent()]


class StyleTransferImageControl(StyleTransferControl):
    title: str = "Style Transfer"
    description: str = (
        "Influences the style, composition, and colors of the generated result."
    )
    content_type: ContentType = ContentType.IMAGE
    supported_contents: List[ControlContent] = [ImageControlContent()]


class FaceReplacementImageControl(FaceReplacementControl):
    title: str = "Face Replacement"
    description: str = (
        "Incorporates a provided face into the generated image. Useful for portraits or character design."
    )
    content_type: ContentType = ContentType.IMAGE
    supported_contents: List[ControlContent] = [ImageControlContent()]


class TransparentBackgroundImageControl(TransparentBackgroundControl):
    title: str = "Transparent Background"
    description: str = "Generates an image with a transparent background."
    content_type: ContentType = ContentType.IMAGE
    supported_contents: List[ControlContent] = [ImageControlContent()]


class RegionalPromptImageControl(RegionalPromptControl):
    title: str = "Regional Prompt"
    description: str = "Marks the areas for applying regional prompts."
    content_type: ContentType = ContentType.IMAGE
    supported_contents: List[ControlContent] = [MaskControlContent()]


class UpscaleImageControl(UpscaleControl):
    title: str = "Upscale"
    description: str = "Increases the resolution of the provided image."
    content_type: ContentType = ContentType.IMAGE
    supported_contents: List[ControlContent] = [ImageControlContent()]


class FaceDetailerImageControl(FaceDetailerControl):
    title: str = "Face Detailer"
    description: str = "Enhances the details of the face in the generated image."
    content_type: ContentType = ContentType.IMAGE
    supported_contents: List[ControlContent] = [ImageControlContent()]


class SeamlessTilingImageControl(SeamlessTilingControl):
    title: str = "Seamless Tiling"
    description: str = "Generates a seamless tiling pattern from the provided image."
    content_type: ContentType = ContentType.IMAGE
    supported_contents: List[ControlContent] = [ImageControlContent()]


class RelightingImageControl(RelightingControl):
    title: str = "Relighting"
    description: str = (
        "Changes the illumination or weather conditions of the generated scene."
    )
    content_type: ContentType = ContentType.IMAGE
    supported_contents: List[ControlContent] = [ImageControlContent()]


class TryOnImageControl(TryOnControl):
    title: str = "Try On"
    description: str = "Try On the clothes on the person in the image."
    content_type: ContentType = ContentType.IMAGE
    supported_contents: List[ControlContent] = [ImageControlContent()]
