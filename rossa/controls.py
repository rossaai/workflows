from pydantic import BaseModel, root_validator
from typing import List, Optional


from .constants import (
    INFLUENCE_FIELD_DEFAULT,
    REGIONAL_PROMPT_ADVANCED_FIELD_ALIAS,
    INFLUENCE_FIELD_ALIAS,
)

from .types import ValueElement, ContentType, ControlType, Option
from .contents import Content
from .fields import BaseFieldInfo, TextAreaField


class ControlValue(Content, ValueElement):
    @property
    def influence(self) -> float:
        return self.get_influence()

    def get_influence(self) -> float:
        return self.get_field(INFLUENCE_FIELD_ALIAS, INFLUENCE_FIELD_DEFAULT)


class ControlContent(BaseModel):
    content_type: ContentType
    is_required: bool = True
    advanced_fields: Optional[List[BaseFieldInfo]] = None

    class Config:
        arbitrary_types_allowed = True


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


class BaseControl(Option):
    supported_contents: List[ControlContent]

    @root_validator(pre=True)
    def validate_supported_contents(cls, values):
        """Validates that the supported contents are valid."""
        if "supported_contents" in values and values["supported_contents"] is not None:
            for content in values["supported_contents"]:
                if not isinstance(content, ControlContent):
                    raise Exception(
                        f"Supported content {content} must be a ControlContent."
                    )

            # if len(values["supported_contents"]) == 0:
            #     raise Exception("Supported contents cannot be empty.")

        return values

    def supports_content(self, content: ContentType) -> bool:
        """Checks if the control supports the given content."""
        return any(
            supported_content.content_type == content
            for supported_content in self.supported_contents
        )

    def supports_image(self) -> bool:
        """Checks if the control supports image content."""
        return self.supports_content(ContentType.IMAGE)

    def supports_video(self) -> bool:
        """Checks if the control supports video content."""
        return self.supports_content(ContentType.VIDEO)

    def supports_audio(self) -> bool:
        """Checks if the control supports audio content."""
        return self.supports_content(ContentType.AUDIO)

    def supports_text(self) -> bool:
        """Checks if the control supports text content."""
        return self.supports_content(ContentType.TEXT)

    def supports_three_d(self) -> bool:
        """Checks if the control supports 3D content."""
        return self.supports_content(ContentType.THREE_D)

    def supports_mask(self) -> bool:
        """Checks if the control supports mask content."""
        return self.supports_content(ContentType.MASK)


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
    description: str = "Try On the clothes on the person in the content."


class OverlayControl(BaseControl):
    value: ControlType = ControlType.CONTROL_OVERLAY
    title: str = "Overlay"
    description: str = "Overlay the image on the generated content."


class EffectControl(BaseControl):
    value: ControlType = ControlType.CONTROL_EFFECT
    title: str = "Effect"
    description: str = "Apply an effect to the generated content."


class ExpandControl(BaseControl):
    value: ControlType = ControlType.CONTROL_EXPAND
    title: str = "Expand"
    description: str = (
        "Expand the generated image in the specified direction (left, right, top, bottom, or all sides) by a given percentage."
    )


class RemoveObjectControl(BaseControl):
    value: ControlType = ControlType.CONTROL_REMOVE_OBJECT
    title: str = "Remove Object"
    description: str = "Remove selected objects or areas from the generated image."


# IMAGE CONTROLSc
class ReferenceImageControl(ReferenceControl):
    title: str = "Reference"
    description: str = (
        "Guides the image generation process. Lower values blend the colors more, while higher values reduce the influence of the reference image."
    )
    supported_contents: List[ControlContent] = [ImageControlContent()]


class InpaintingImageControl(InpaintingControl):
    title: str = "Inpainting"
    description: str = "Defines areas to be modified in the generated image."
    supported_contents: List[ControlContent] = [
        ImageControlContent(is_required=False),
        MaskControlContent(),
    ]


class CannyImageControl(CannyControl):
    title: str = "Canny Edge Detection"
    description: str = "Emphasizes edges for sketch-to-image generation."
    supported_contents: List[ControlContent] = [ImageControlContent()]


class LineArtImageControl(LineArtControl):
    title: str = "Line Guide"
    description: str = (
        "Extracts and guides the generation based on the contours and fine details of the provided image, without considering colors or other elements. Useful for sketch-to-image generation and line-based guidance."
    )
    supported_contents: List[ControlContent] = [ImageControlContent()]


class PoseImageControl(PoseControl):
    title: str = "Pose Guide"
    description: str = (
        "Incorporates a specified pose into the generated image. Useful for complex poses."
    )
    supported_contents: List[ControlContent] = [ImageControlContent()]


class DepthImageControl(DepthControl):
    title: str = "Depth Guide"
    description: str = (
        "Incorporates depth information into the generated image. Useful for 3D effects."
    )
    supported_contents: List[ControlContent] = [ImageControlContent()]


class StyleTransferImageControl(StyleTransferControl):
    title: str = "Style Transfer"
    description: str = (
        "Influences the style, composition, and colors of the generated result."
    )
    supported_contents: List[ControlContent] = [ImageControlContent()]


class FaceReplacementImageControl(FaceReplacementControl):
    title: str = "Face Replacement"
    description: str = (
        "Incorporates a provided face into the generated image. Useful for portraits or character design."
    )
    supported_contents: List[ControlContent] = [ImageControlContent()]


class TransparentBackgroundImageControl(TransparentBackgroundControl):
    title: str = "Transparent Background"
    description: str = "Generates an image with a transparent background."
    supported_contents: List[ControlContent] = [ImageControlContent()]


class RegionalPromptImageControl(RegionalPromptControl):
    title: str = "Regional Prompt"
    description: str = "Marks the areas for applying regional prompts."
    supported_contents: List[ControlContent] = [MaskControlContent()]


class UpscaleImageControl(UpscaleControl):
    title: str = "Upscale"
    description: str = "Increases the resolution of the provided image."
    supported_contents: List[ControlContent] = [ImageControlContent()]


class FaceDetailerImageControl(FaceDetailerControl):
    title: str = "Face Detailer"
    description: str = "Enhances the details of the face in the generated image."
    supported_contents: List[ControlContent] = [ImageControlContent()]


class SeamlessTilingImageControl(SeamlessTilingControl):
    title: str = "Seamless Tiling"
    description: str = "Generates a seamless tiling pattern from the provided image."
    supported_contents: List[ControlContent] = [ImageControlContent()]


class RelightingImageControl(RelightingControl):
    title: str = "Relighting"
    description: str = (
        "Changes the illumination or weather conditions of the generated scene."
    )
    supported_contents: List[ControlContent] = [ImageControlContent()]


class TryOnImageControl(TryOnControl):
    title: str = "Try On"
    description: str = "Try On the clothes on the person in the image."
    supported_contents: List[ControlContent] = [ImageControlContent()]


class OverlayImageControl(OverlayControl):
    title: str = "Image Overlay"
    description: str = "Overlay the image on the generated image."
    supported_contents: List[ControlContent] = [ImageControlContent()]


class EffectImageControl(EffectControl):
    title: str = "Image Effect"
    description: str = "Apply an effect to the generated image."
    supported_contents: List[ControlContent] = [ImageControlContent()]


class RemoveObjectImageControl(RemoveObjectControl):
    title: str = "Remove Object"
    description: str = (
        "Removes selected objects or areas from the generated image, allowing for targeted object removal and image cleanup."
    )
    supported_contents: List[ControlContent] = [
        ImageControlContent(),
        MaskControlContent(),
    ]


class ExpandImageControl(ExpandControl):
    title: str = "Expand Image"
    description: str = (
        "Expands the generated image in the specified direction (left, right, top, bottom, or all sides) by a given percentage, allowing for seamless image extension and canvas resizing."
    )
    supported_contents: List[ControlContent] = [ImageControlContent()]
