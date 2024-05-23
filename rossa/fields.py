from pydantic import Field as PydanticField
from pydantic.fields import FieldInfo
from typing import Any, List, Literal, Optional, Union

from .fields_conditionals import ShowFieldIfValue
from .types import FormatType, GeneratorType, Option, FieldType


BaseFieldInfo = FieldInfo

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
    alias: Optional[str] = None,
    placeholder: str = "",
    options: Optional[List[Option]] = None,
    default: Optional[Any] = None,
    default_generator_type: Optional[GeneratorType] = None,
    show_if: Optional[Union[ShowFieldIfValue, List[ShowFieldIfValue]]] = None,
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

    if default is not None and default_generator_type is not None:
        raise Exception("Field cannot have both default and default_generator_type.")

    if default_generator_type is not None and not isinstance(
        default_generator_type, GeneratorType
    ):
        raise Exception("default_generator_type must be a GeneratorType.")

    # validate if type is in FieldType
    if type not in set(FieldType):
        raise Exception("Field type must be in FieldType.")

    def default_factory():
        if default_generator_type:
            return default_generator_type.generate(kwargs.get("ge"), kwargs.get("le"))
        return None

    return PydanticField(
        alias=alias,
        default_factory=(default_factory if default_generator_type else None),
        title=title,
        type=type,
        description=description,
        placeholder=placeholder,
        options=options,
        show_if=show_if,
        **kwargs,
    )


def TextField(
    title: str,
    description: str,
    placeholder: str = "",
    alias: Optional[str] = None,
    default: Optional[str] = None,
    default_generator_type: Optional[GeneratorType] = None,
    show_if: Optional[Union[ShowFieldIfValue, List[ShowFieldIfValue]]] = None,
    **kwargs,
):
    return BaseField(
        alias=alias,
        type=FieldType.TEXT.value,
        title=title,
        description=description,
        placeholder=placeholder,
        default=default,
        default_generator_type=default_generator_type,
        show_if=show_if,
        **kwargs,
    )


def TextAreaField(
    title: str,
    description: str,
    alias: Optional[str] = None,
    placeholder: str = "",
    show_if: Optional[Union[ShowFieldIfValue, List[ShowFieldIfValue]]] = None,
    default: Optional[str] = None,
    default_generator_type: Optional[GeneratorType] = None,
    **kwargs,
):
    return BaseField(
        alias=alias,
        type=FieldType.TEXTAREA.value,
        title=title,
        description=description,
        placeholder=placeholder,
        show_if=show_if,
        default=default,
        default_generator_type=default_generator_type,
        **kwargs,
    )


def NumberField(
    title: str,
    description: str,
    alias: Optional[str] = None,
    placeholder: str = "",
    min: Optional[float] = None,
    max: Optional[float] = None,
    step: Optional[float] = None,
    format_type: FormatType = FormatType.DECIMAL,
    default: Optional[float] = None,
    default_generator_type: Optional[GeneratorType] = None,
    show_if: Optional[Union[ShowFieldIfValue, List[ShowFieldIfValue]]] = None,
    **kwargs,
):
    return BaseField(
        alias=alias,
        type=FieldType.NUMBER.value,
        title=title,
        description=description,
        placeholder=placeholder,
        ge=min,
        le=max,
        step=step,
        format_type=format_type,
        default=default,
        default_generator_type=default_generator_type,
        show_if=show_if,
        **kwargs,
    )


def IntegerField(
    title: str,
    description: str,
    alias: Optional[str] = None,
    placeholder: str = "",
    step: int = 1,
    default: Optional[int] = None,
    min: Optional[int] = None,
    max: Optional[int] = None,
    default_generator_type: Optional[GeneratorType] = None,
    show_if: Optional[Union[ShowFieldIfValue, List[ShowFieldIfValue]]] = None,
    **kwargs,
):
    step = int(step)

    return BaseField(
        alias=alias,
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
        show_if=show_if,
        **kwargs,
    )


def SliderField(
    title: str,
    description: str,
    min: float,
    max: float,
    alias: Optional[str] = None,
    step: Optional[float] = None,
    placeholder: str = "",
    format_type: FormatType = FormatType.DECIMAL,
    default: Optional[float] = None,
    default_generator_type: Optional[GeneratorType] = None,
    show_if: Optional[Union[ShowFieldIfValue, List[ShowFieldIfValue]]] = None,
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
        alias=alias,
        type=FieldType.SLIDER.value,
        title=title,
        description=description,
        placeholder=placeholder,
        ge=min,
        le=max,
        step=step,
        format_type=format_type,
        default=default,
        default_generator_type=default_generator_type,
        show_if=show_if,
        **kwargs,
    )


def PercentageSliderField(
    title: str,
    description: str,
    alias: Optional[str] = None,
    placeholder: str = "",
    min: float = 0,
    max: float = 100,
    step: float = 1,
    default: Optional[float] = None,
    default_generator_type: Optional[GeneratorType] = None,
    show_if: Optional[Union[ShowFieldIfValue, List[ShowFieldIfValue]]] = None,
    **kwargs,
):
    return SliderField(
        alias=alias,
        title=title,
        description=description,
        placeholder=placeholder,
        min=min,
        max=max,
        step=step,
        format_type=FormatType.PERCENTAGE,
        default=default,
        default_generator_type=default_generator_type,
        show_if=show_if,
        **kwargs,
    )


def CheckboxField(
    title: str,
    description: str,
    alias: Optional[str] = None,
    placeholder: str = "",
    default: bool = False,
    show_if: Optional[Union[ShowFieldIfValue, List[ShowFieldIfValue]]] = None,
    **kwargs,
):
    return BaseField(
        alias=alias,
        type=FieldType.CHECKBOX.value,
        title=title,
        description=description,
        placeholder=placeholder,
        default=default,
        show_if=show_if,
        **kwargs,
    )


def SelectField(
    title: str,
    description: str,
    options: List[Option],
    alias: Optional[str] = None,
    placeholder: str = "",
    default: Optional[str] = None,
    default_generator_type: Optional[GeneratorType] = None,
    show_if: Optional[Union[ShowFieldIfValue, List[ShowFieldIfValue]]] = None,
    **kwargs,
):
    return BaseField(
        alias=alias,
        type=FieldType.SELECT.value,
        title=title,
        description=description,
        placeholder=placeholder,
        options=options,
        default=default,
        default_generator_type=default_generator_type,
        show_if=show_if,
        **kwargs,
    )
