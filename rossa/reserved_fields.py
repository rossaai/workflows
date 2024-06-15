from typing import List, Optional

from .constants import (
    CONTROLS_FIELD_ALIAS,
    NEGATIVE_PROMPT_FIELD_ALIAS,
    PROMPT_FIELD_ALIAS,
)
from .controls import BaseControl, ControlValue
from .fields import BaseField
from .types import FieldType, GeneratorType
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
    options: List[BaseControl] = [],
    default: List[ControlValue] = [],
    alias: Optional[str] = CONTROLS_FIELD_ALIAS,
    default_generator_type: Optional[GeneratorType] = None,
    show_if: Optional[FieldsConditionals] = None,
    disable_if: Optional[FieldsConditionals] = None,
    **kwargs,
):
    for option in options:
        if not isinstance(option, BaseControl):
            raise Exception("Control options must be a list of BaseControl.")

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
