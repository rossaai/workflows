from pydantic import BaseModel, Field as PydanticField
from typing import List, Optional, Union
from .types import Content, Option, ApplicableFor, ContentType, ControlType
from .image_conversion_utils import url_to_pil_image, url_to_cv2_image


class ControlValue(Content):
    influence: float
    content: str
    mask: Optional[str] = None

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


class ApplicableForRequirements(BaseModel):
    """
    Represents the requirements for a specific applicability level.

    Attributes:
        required (bool): Indicates whether the requirement is mandatory. Default is False.
        editable (bool): Indicates whether the requirement is editable. Default is True.

    Examples:
        >>> reqs = ApplicableForRequirements(required=True, editable=False)
        >>> print(reqs.required)
        True
        >>> print(reqs.editable)
        False
    """

    required: bool = False
    editable: bool = True


class ControlRequirements(BaseModel):
    """
    Represents the control requirements for different applicability levels.

    Attributes:
        all (Optional[ApplicableForRequirements]): The requirements applicable for all levels.
        parent (Optional[ApplicableForRequirements]): The requirements applicable for the parent level.
        child (Optional[ApplicableForRequirements]): The requirements applicable for the child level.

    Examples:
        >>> control_reqs = ControlRequirements(
        ...     all=ApplicableForRequirements(required=True),
        ...     parent=ApplicableForRequirements(editable=False),
        ...     child=ApplicableForRequirements(required=False, editable=True)
        ... )
        >>> print(control_reqs.all.required)
        True
        >>> print(control_reqs.parent.editable)
        False
        >>> print(control_reqs.child.required)
        False
    """

    all: Optional[ApplicableForRequirements]
    parent: Optional[ApplicableForRequirements]
    child: Optional[ApplicableForRequirements]


class BaseControl(Option):
    value: Union[ControlType, str]
    content_type: ContentType
    applicable_for: List[ApplicableFor] = PydanticField(
        default=[ApplicableFor.ALL],
        title="Applicable For",
        description="The control is applicable for the following elements.",
    )
    requirements: Optional[ControlRequirements] = None


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


# IMAGE CONTROLS
class InputImageControl(InputControl):
    title: str = "Source Image"
    description: str = "Provide an input image for Image generation."
    content_type: ContentType = ContentType.IMAGE


class MaskImageControl(MaskControl):
    title: str = "Mask"
    description: str = "Define areas to be modified for Image generation."
    content_type: ContentType = ContentType.IMAGE


class LineArtImageControl(LineArtControl):
    title: str = "Line Art"
    description: str = (
        "Emphasize lines for constraining the generated image. Useful for sketch-to-image generation."
    )
    content_type: ContentType = ContentType.IMAGE


class CannyImageControl(CannyControl):
    title: str = "Edge Detection"
    description: str = "Emphasize edges for sketch-to-image generation."
    content_type: ContentType = ContentType.IMAGE


class PoseImageControl(PoseControl):
    title: str = "Pose Guide"
    description: str = "Specify a pose to be incorporated into the generated image."
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
