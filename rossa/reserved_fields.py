from typing import List, Optional, Union

from .constants import (
    CONTROLS_FIELD_ALIAS,
    INFLUENCE_FIELD_ALIAS,
    INFLUENCE_FIELD_DEFAULT,
    NEGATIVE_PROMPT_FIELD_ALIAS,
    PROMPT_FIELD_ALIAS,
)
from .controls import BaseControl, ControlValue
from .fields import BaseField, SliderField
from .types import FieldType, FormatType, GeneratorType, Option
from .fields_conditionals import FieldsConditionals


def PromptField(
    title: str = "Prompt",
    description: str = "Prompt for the model.",
    placeholder: str = "What do you want to create?",
    default: str = "",
    alias: Optional[str] = PROMPT_FIELD_ALIAS,
    default_generator_type: Optional[GeneratorType] = None,
    multiple: bool = False,
    show_if: Optional[FieldsConditionals] = None,
    disable_if: Optional[FieldsConditionals] = None,
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
    show_if: Optional[FieldsConditionals] = None,
    disable_if: Optional[FieldsConditionals] = None,
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
    options: List[Union[BaseControl, Option]] = [],
    default: List[ControlValue] = [],
    alias: Optional[str] = CONTROLS_FIELD_ALIAS,
    default_generator_type: Optional[GeneratorType] = None,
    show_if: Optional[FieldsConditionals] = None,
    disable_if: Optional[FieldsConditionals] = None,
    **kwargs,
):
    for option in options:
        if not isinstance(option, (BaseControl, Option)):
            raise Exception("Control options must be a list of BaseControl or Option.")

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


def InfluenceField(**kwargs):
    return SliderField(
        alias=INFLUENCE_FIELD_ALIAS,
        title="Influence",
        description="The percentage of influence the control has on the generation.",
        min=0.0,
        max=2.0,
        default=INFLUENCE_FIELD_DEFAULT,
        format_type=FormatType.PERCENTAGE,
        kwargs=kwargs,
    )
