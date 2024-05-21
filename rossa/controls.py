from pydantic import BaseModel, Field as PydanticField, root_validator
from typing import Any, Dict, List, Optional, Union

from fields import BaseField
from .types import Content, Option, ApplicableElement, ContentType, ControlType
from .image_conversion_utils import url_to_pil_image, url_to_cv2_image


class ControlValue(Content):
    influence: float
    content: str
    mask: Optional[str] = None

    advanced_fields: Optional[Dict[str, Any]] = None

    def get_advanced_field(self, field_name: str, default: Any = None):
        """Gets an advanced field by name."""
        if self.advanced_fields is None:
            return default

        return self.advanced_fields.get(field_name, default)

    def has_mask(self):
        """Checks if the control has a mask."""
        return self.mask is not None

    def to_pil_image(self):
        """Converts a URL to a PIL image."""
        img = url_to_pil_image(self.content)

        if img is None:
            raise Exception("Invalid image URL. Please provide a valid image URL.")

        return img

    def to_cv2_image(self):
        """Converts a URL to a cv2 image. Remember to `.apt_install("ffmpeg", "libsm6", "libxext6")` to your `rossa.Image`."""
        img = url_to_cv2_image(self.content)

        if img is None:
            raise Exception("Invalid image URL. Please provide a valid image URL.")

        return img

    def mask_to_pil_image(self):
        """Converts a URL to a PIL image."""
        if not self.has_mask():
            raise Exception("Mask URL is not provided.")

        img = url_to_pil_image(self.mask)

        if img is None:
            raise Exception("Invalid image URL. Please provide a valid image URL.")

        return img

    def mask_to_cv2_image(self):
        """Converts a URL to a cv2 image. Remember to `.apt_install("ffmpeg", "libsm6", "libxext6")` to your `rossa.Image`."""
        if not self.has_mask():
            raise Exception("Mask URL is not provided.")

        img = url_to_cv2_image(self.mask)

        if img is None:
            raise Exception("Invalid image URL. Please provide a valid image URL.")

        return img


class RequirementApplicability(BaseModel):
    """
    Represents the applicability of specific requirements.

    Attributes:
        is_required (bool): Indicates whether the requirement is mandatory. Default is False.
        supports_influence (bool): Indicates whether the requirement supports influence. Default is True.
        supports_mask (bool): Indicates whether the requirement supports masking. Default is False.
        requires_mask (bool): Indicates whether the requirement requires masking. Default is False.

    Examples:
        >>> reqs = RequirementApplicability(is_required=True, is_editable=False)
        >>> print(reqs.is_required)
        True
        >>> print(reqs.is_editable)
        False
    """

    is_required: bool = False
    supports_influence: bool = True
    supports_mask: bool = False
    requires_mask: bool = False


class ApplicabilityControlRequirements(BaseModel):
    """
    Represents the control requirements for different applicability levels.

    Attributes:
        all_levels (Optional[RequirementApplicability]): The requirements applicable for all levels.
        parent_level (Optional[RequirementApplicability]): The requirements applicable for the parent level.
        child_level (Optional[RequirementApplicability]): The requirements applicable for the child level.

    Examples:
        >>> control_reqs = ApplicabilityApplicabilityControlRequirements(
        ...     all_levels=RequirementApplicability(is_required=True),
        ...     parent_level=RequirementApplicability(is_editable=False),
        ...     child_level=RequirementApplicability(is_required=False, is_editable=True)
        ... )
        >>> print(control_reqs.all_levels.is_required)
        True
        >>> print(control_reqs.parent_level.is_editable)
        False
        >>> print(control_reqs.child_level.is_required)
        False
    """

    all_levels: Optional[RequirementApplicability]
    parent_level: Optional[RequirementApplicability]
    child_level: Optional[RequirementApplicability]


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
    applicable_elements: List[ApplicableElement] = PydanticField(
        default=[ApplicableElement.ALL],
        title="Applicable Elements",
        description="The control option is applicable for the following elements.",
    )
    requirements: Optional[ApplicabilityControlRequirements] = None
    advanced_fields: Optional[List[BaseField]] = None

    @root_validator(pre=True)
    def validate_every_advanced_field_has_alias(cls, values):
        """Validates that every advanced field has an alias."""
        if "advanced_fields" in values and values["advanced_fields"] is not None:
            for field in values["advanced_fields"]:
                if not hasattr(field, "alias") or field.alias is None:
                    raise Exception(f"Advanced field {field} must have an alias.")

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


class CompositionTransferControl(BaseControl):
    value: ControlType = ControlType.CONTROL_COMPOSITION_TRANSFER
    title: str = "Composition Transfer"
    description: str = "Incorporates composition into your generation."


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


class MaskImageControl(MaskControl):
    title: str = "Mask"
    description: str = "Define areas to be modified for Image generation."
    content_type: ContentType = ContentType.IMAGE


class CannyImageControl(CannyControl):
    title: str = "Edge Detection"
    description: str = "Emphasize edges for sketch-to-image generation."
    content_type: ContentType = ContentType.IMAGE


class LineArtImageControl(LineArtControl):
    title: str = "Line Art"
    description: str = (
        "Emphasize lines for constraining the generated image. Very useful for sketch-to-image generation."
    )
    content_type: ContentType = ContentType.IMAGE


class PoseImageControl(PoseControl):
    title: str = "Pose Guide"
    description: str = "Specify a pose to be incorporated into the generated image."
    content_type: ContentType = ContentType.IMAGE


class DepthImageControl(DepthControl):
    title: str = "Depth"
    description: str = "Incorporate depth into the generated image."
    content_type: ContentType = ContentType.IMAGE


class StyleTransferImageControl(StyleTransferControl):
    title: str = "Style Image"
    description: str = (
        "Use an image to influence the style, composition, and colors of the generated result."
    )
    content_type: ContentType = ContentType.IMAGE


class CompositionTransferImageControl(CompositionTransferControl):
    title: str = "Composition Transfer"
    description: str = "Incorporate composition into the generated image."
    content_type: ContentType = ContentType.IMAGE


class FaceReplacementImageControl(FaceReplacementControl):
    title: str = "Face Replacement"
    description: str = "Replace faces in the generated image."
    content_type: ContentType = ContentType.IMAGE


class TransparentBackgroundImageControl(TransparentBackgroundControl):
    title: str = "Transparent Background"
    description: str = "When generating it keeps the background transparent"
    content_type: ContentType = ContentType.IMAGE
