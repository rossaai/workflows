from pydantic import Field as PydanticField
from typing import List, Literal, Optional

from .performances import BasePerformance
from .controls import BaseControl
from .types import Option, FieldType, PerformanceType


FieldTypeLiteral = Literal[
    "text",
    "textarea",
    "number",
    "integer",
    "checkbox",
    "select",
    "prompt",
    "negative_prompt",
    "performance",
    "controls",
]


def BaseField(
    title: str,
    type: FieldTypeLiteral,
    description: str,
    alias: str = None,
    placeholder: str = "",
    options: Optional[List[Option]] = None,
    **kwargs,
):
    if options:
        for option in options:
            if not isinstance(option, Option):
                raise Exception("Field options must be a list of Option.")

    if type == FieldType.SELECT and not options:
        raise Exception("Select fields must have options.")

    if type == FieldType.PERFORMANCE and not options:
        raise Exception("Performance fields must have options.")

    if type == FieldType.CONTROLS and not options:
        raise Exception("Controls fields must have options.")

    # validate if type is in FieldType
    if type not in set(FieldType):
        raise Exception("Field type must be in FieldType.")

    return PydanticField(
        title=title,
        type=type,
        alias=alias,
        description=description,
        placeholder=placeholder,
        options=options,
        **kwargs,
    )


def TextField(
    title: str,
    description: str,
    placeholder: str = "",
    **kwargs,
):
    return BaseField(
        type=FieldType.TEXT.value,
        title=title,
        description=description,
        placeholder=placeholder,
        **kwargs,
    )


def TextAreaField(
    title: str,
    description: str,
    placeholder: str = "",
    **kwargs,
):
    return BaseField(
        type=FieldType.TEXTAREA.value,
        title=title,
        description=description,
        placeholder=placeholder,
        **kwargs,
    )


def NumberField(
    title: str,
    description: str,
    placeholder: str = "",
    min: Optional[float] = None,
    max: Optional[float] = None,
    step: Optional[float] = None,
    **kwargs,
):
    return BaseField(
        type=FieldType.NUMBER.value,
        title=title,
        description=description,
        placeholder=placeholder,
        ge=min,
        le=max,
        step=step,
        **kwargs,
    )


def IntegerField(
    title: str,
    description: str,
    placeholder: str = "",
    min: Optional[int] = None,
    max: Optional[int] = None,
    step: Optional[int] = None,
    **kwargs,
):
    return BaseField(
        type=FieldType.INTEGER.value,
        title=title,
        description=description,
        placeholder=placeholder,
        ge=min,
        le=max,
        step=step,
        **kwargs,
    )


def CheckboxField(
    title: str,
    description: str,
    placeholder: str = "",
    **kwargs,
):
    return BaseField(
        type=FieldType.CHECKBOX.value,
        title=title,
        description=description,
        placeholder=placeholder,
        default=False,
        **kwargs,
    )


def SelectField(
    title: str,
    description: str,
    options: List[Option],
    placeholder: str = "",
    **kwargs,
):
    return BaseField(
        type=FieldType.SELECT.value,
        title=title,
        description=description,
        placeholder=placeholder,
        options=options,
        default=[],
        **kwargs,
    )


# RESERVED FIELDS
def PromptField(
    title: str = "Prompt",
    description: str = "Prompt for the model.",
    placeholder: str = "What do you want to create?",
    **kwargs,
):
    return BaseField(
        type=FieldType.PROMPT.value,
        alias="prompt",
        title=title,
        description=description,
        placeholder=placeholder,
        default="",
        **kwargs,
    )


def NegativePromptField(
    title: str = "Negative Prompt",
    description: str = "Negative prompt for the model.",
    placeholder: str = "What do you want to avoid?",
    **kwargs,
):
    return BaseField(
        type=FieldType.NEGATIVE_PROMPT.value,
        alias="negative_prompt",
        title=title,
        description=description,
        placeholder=placeholder,
        default="",
        **kwargs,
    )


def PerformanceField(
    title: str = "Performance",
    description: str = "Performance settings.",
    options: List[BasePerformance] = [],
    **kwargs,
):
    for option in options:
        if not isinstance(option, BasePerformance):
            raise Exception("Performance options must be a list of BasePerformance.")

    return BaseField(
        type=FieldType.PERFORMANCE.value,
        alias="performance",
        default=[],
        title=title,
        description=description,
        options=options,
        **kwargs,
    )


def ControlsField(
    title: str = "Controls",
    description: str = "List of controls.",
    options: List[BaseControl] = [],
    **kwargs,
):
    for option in options:
        if not isinstance(option, BaseControl):
            raise Exception("Control options must be a list of BaseControl.")

    return BaseField(
        type=FieldType.CONTROLS.value,
        alias="controls",
        default=[],
        title=title,
        description=description,
        options=options,
        **kwargs,
    )
