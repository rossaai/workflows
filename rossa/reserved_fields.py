from typing import List, Optional, Union
from pydantic import BaseModel
from .constants import (
    CONTROLS_FIELD_ALIAS,
    INFLUENCE_FIELD_ALIAS,
    INFLUENCE_FIELD_DEFAULT,
    NEGATIVE_PROMPT_FIELD_ALIAS,
    PROMPT_FIELD_ALIAS,
)
from .fields import BaseField, SliderField, BaseFieldInfo, Option
from .types import ContentType, FieldType, FormatType, GeneratorType
from .field_conditionals import FieldConditionals
from .reserved_field_values import ControlValue


class ControlContent(BaseModel):
    type: ContentType
    required: bool = True
    fields: Optional[List[BaseFieldInfo]] = None
    advanced_fields: Optional[List[BaseFieldInfo]] = None

    class Config:
        arbitrary_types_allowed = True


class ImageControlContent(ControlContent):
    type: ContentType = ContentType.IMAGE


class VideoControlContent(ControlContent):
    type: ContentType = ContentType.VIDEO


class AudioControlContent(ControlContent):
    type: ContentType = ContentType.AUDIO


class TextControlContent(ControlContent):
    type: ContentType = ContentType.TEXT


class ThreeDControlContent(ControlContent):
    type: ContentType = ContentType.THREE_D


class MaskControlContent(ControlContent):
    type: ContentType = ContentType.MASK


class ControlOption(Option):
    input_contents: Optional[List[ControlContent]] = None
    output_contents: Optional[List[ControlContent]] = None

    def supports_content(self, content: ContentType) -> bool:
        """Checks if the control supports the given content."""
        return any(
            supported_content.type == content
            for supported_content in self.input_contents
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


def PromptField(
    title: str = "Prompt",
    description: str = "Prompt for the model.",
    placeholder: str = "Describe what would you want to create",
    default: str = "",
    alias: Optional[str] = PROMPT_FIELD_ALIAS,
    default_generator_type: Optional[GeneratorType] = None,
    multiple: bool = False,
    show_if: Optional[FieldConditionals] = None,
    disable_if: Optional[FieldConditionals] = None,
    **kwargs,
):
    return BaseField(
        type=FieldType.PROMPT.value,
        alias=alias,
        title=title,
        description=description,
        placeholder=placeholder,
        default=default,
        default_generator_type=default_generator_type,
        multiple=multiple,
        show_if=show_if,
        disable_if=disable_if,
        **kwargs,
    )


def NegativePromptField(
    title: str = "Negative Prompt",
    description: str = "Negative prompt for the model.",
    placeholder: str = "What do you want to avoid?",
    default: str = "",
    alias: Optional[str] = NEGATIVE_PROMPT_FIELD_ALIAS,
    default_generator_type: Optional[GeneratorType] = None,
    multiple: bool = False,
    show_if: Optional[FieldConditionals] = None,
    disable_if: Optional[FieldConditionals] = None,
    **kwargs,
):
    return BaseField(
        type=FieldType.NEGATIVE_PROMPT.value,
        alias=alias,
        title=title,
        description=description,
        placeholder=placeholder,
        default=default,
        default_generator_type=default_generator_type,
        multiple=multiple,
        show_if=show_if,
        disable_if=disable_if,
        **kwargs,
    )


def ControlsField(
    title: str = "Controls",
    description: str = "List of controls.",
    options: List[Union[ControlOption, Option]] = [],
    default: List[ControlValue] = [],
    alias: Optional[str] = CONTROLS_FIELD_ALIAS,
    default_generator_type: Optional[GeneratorType] = None,
    show_if: Optional[FieldConditionals] = None,
    disable_if: Optional[FieldConditionals] = None,
    **kwargs,
):
    for option in options:
        if not isinstance(option, (ControlOption, Option)):
            raise Exception(
                "Control options must be a list of ControlOption or Option."
            )

    return BaseField(
        type=FieldType.CONTROLS.value,
        alias=alias,
        title=title,
        default=default,
        description=description,
        options=options,
        default_generator_type=default_generator_type,
        multiple=True,
        show_if=show_if,
        disable_if=disable_if,
        **kwargs,
    )


def InfluenceField(
    alias=INFLUENCE_FIELD_ALIAS,
    title="Influence",
    description="El porcentaje de influencia que el control tiene sobre la generación.",
    min=0.0,
    max=2.0,
    default=INFLUENCE_FIELD_DEFAULT,
    format_type=FormatType.PERCENTAGE,
    **kwargs,
):
    return SliderField(
        alias=alias,
        title=title,
        description=description,
        min=min,
        max=max,
        default=default,
        format_type=format_type,
        **kwargs,
    )
