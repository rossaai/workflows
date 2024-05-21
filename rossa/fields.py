from pydantic import Field as PydanticField
from typing import Any, List, Literal, Optional
from .types import FormatType, GeneratorType, Option, FieldType


FieldTypeLiteral = Literal[
    "text",
    "textarea",
    "number",
    "slider",
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

    if "default" in kwargs and "default_generator_type" in kwargs:
        raise Exception("Field cannot have both default and default_generator_type.")

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
    format_type: FormatType = FormatType.DECIMAL,
    default_generator_type: Optional[GeneratorType] = None,
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
        format_type=format_type,
        default_generator_type=default_generator_type,
        **kwargs,
    )


def IntegerField(
    title: str,
    description: str,
    placeholder: str = "",
    step: int = 1,
    default: Optional[int] = None,
    min: Optional[int] = None,
    max: Optional[int] = None,
    default_generator_type: Optional[GeneratorType] = None,
    **kwargs,
):
    step = int(step)

    return BaseField(
        type=FieldType.NUMBER.value,
        title=title,
        description=description,
        placeholder=placeholder,
        ge=min,
        le=max,
        step=step,
        format_type=FormatType.INTEGER,
        default_generator_type=default_generator_type,
        default=default,
        **kwargs,
    )


def SliderField(
    title: str,
    description: str,
    min: float,
    max: float,
    step: Optional[float] = None,
    placeholder: str = "",
    format_type: FormatType = FormatType.DECIMAL,
    **kwargs,
):
    if min > max:
        raise Exception("Minimum value must be less than maximum value.")

    if step and step <= 0:
        raise Exception("Step value must be greater than 0.")

    if min is None:
        raise Exception("Minimum value must be provided.")

    if max is None:
        raise Exception("Maximum value must be provided.")

    return BaseField(
        type=FieldType.SLIDER.value,
        title=title,
        description=description,
        placeholder=placeholder,
        ge=min,
        le=max,
        step=step,
        format_type=format_type,
        **kwargs,
    )


def PercentageSliderField(
    title: str,
    description: str,
    placeholder: str = "",
    min: float = 0,
    max: float = 100,
    step: float = 1,
    **kwargs,
):
    return SliderField(
        title=title,
        description=description,
        placeholder=placeholder,
        min=min,
        max=max,
        step=step,
        format_type=FormatType.PERCENTAGE,
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
