from pydantic import BaseModel, Field as PydanticField, root_validator
from pydantic.fields import FieldInfo
from typing import Any, List, Optional

from .field_values import SelectFieldValue

from .field_conditionals import FieldConditionals
from .types import (
    FormatType,
    GeneratorType,
    FieldType,
)
from .constants import SAFE_DEFAULT_FIELD_KEY


BaseFieldInfo = FieldInfo


class Option(BaseModel):
    value: str
    title: str
    group: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[List[FieldInfo]] = None
    advanced_fields: Optional[List[FieldInfo]] = None
    max: Optional[int] = None

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


def BaseField(
    title: str,
    type: FieldType,
    description: str,
    alias: Optional[str] = None,
    placeholder: str = "",
    options: Optional[List[Option]] = None,
    default: Optional[Any] = None,
    default_generator_type: Optional[GeneratorType] = None,
    show_if: Optional[FieldConditionals] = None,
    disable_if: Optional[FieldConditionals] = None,
    **kwargs,
):
    if options:
        for option in options:
            if not isinstance(option, Option):
                raise Exception("Field options must be a list of Option.")

    if (
        type
        in [
            FieldType.SELECT,
            FieldType.RADIO,
            FieldType.DYNAMIC_FORM,
            FieldType.CONTROLS,
        ]
        and not options
    ):
        raise Exception(
            "Select, Radio, Dynamic Form and Controls fields must have options."
        )

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
        if default_generator_type is not None:
            return default_generator_type.generate(kwargs.get("ge"), kwargs.get("le"))

        return default

    if default is not None:
        kwargs = kwargs or {}

        kwargs[SAFE_DEFAULT_FIELD_KEY] = default

    return PydanticField(
        alias=alias,
        default_factory=(
            default_factory
            if isinstance(default_generator_type, GeneratorType) or default is not None
            else None
        ),
        title=title,
        type=type,
        description=description,
        placeholder=placeholder,
        options=options,
        default_generator_type=default_generator_type,
        show_if=show_if,
        disable_if=disable_if,
        **kwargs,
    )


def TextField(
    title: str,
    description: str,
    placeholder: str = "",
    alias: Optional[str] = None,
    default: Optional[str] = None,
    default_generator_type: Optional[GeneratorType] = None,
    show_if: Optional[FieldConditionals] = None,
    disable_if: Optional[FieldConditionals] = None,
    **kwargs,
):
    return BaseField(
        alias=alias,
        type=FieldType.TEXT,
        title=title,
        description=description,
        placeholder=placeholder,
        default=default,
        default_generator_type=default_generator_type,
        show_if=show_if,
        disable_if=disable_if,
        **kwargs,
    )


def TextAreaField(
    title: str,
    description: str,
    alias: Optional[str] = None,
    placeholder: str = "",
    show_if: Optional[FieldConditionals] = None,
    disable_if: Optional[FieldConditionals] = None,
    default: Optional[str] = None,
    default_generator_type: Optional[GeneratorType] = None,
    **kwargs,
):
    return BaseField(
        alias=alias,
        type=FieldType.TEXTAREA,
        title=title,
        description=description,
        placeholder=placeholder,
        show_if=show_if,
        disable_if=disable_if,
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
    show_if: Optional[FieldConditionals] = None,
    disable_if: Optional[FieldConditionals] = None,
    **kwargs,
):
    return BaseField(
        alias=alias,
        type=FieldType.NUMBER,
        title=title,
        description=description,
        placeholder=placeholder,
        ge=min,
        le=max,
        format_type=format_type,
        default=default,
        default_generator_type=default_generator_type,
        show_if=show_if,
        disable_if=disable_if,
        min=min,
        max=max,
        step=step,
        **kwargs,
    )


def IntegerField(
    title: str,
    description: str,
    alias: Optional[str] = None,
    placeholder: str = "",
    default: Optional[int] = None,
    min: Optional[int] = None,
    max: Optional[int] = None,
    step: int = 1,
    default_generator_type: Optional[GeneratorType] = None,
    show_if: Optional[FieldConditionals] = None,
    disable_if: Optional[FieldConditionals] = None,
    **kwargs,
):
    step = int(step)

    return BaseField(
        alias=alias,
        type=FieldType.NUMBER,
        title=title,
        description=description,
        placeholder=placeholder,
        ge=min,
        le=max,
        format_type=FormatType.INTEGER,
        default_generator_type=default_generator_type,
        default=default,
        show_if=show_if,
        disable_if=disable_if,
        min=min,
        max=max,
        step=step,
        **kwargs,
    )


def SliderField(
    title: str,
    description: str,
    min: float,
    max: float,
    step: Optional[float] = None,
    alias: Optional[str] = None,
    placeholder: str = "",
    format_type: FormatType = FormatType.DECIMAL,
    default: Optional[float] = None,
    default_generator_type: Optional[GeneratorType] = None,
    show_if: Optional[FieldConditionals] = None,
    disable_if: Optional[FieldConditionals] = None,
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
        type=FieldType.SLIDER,
        title=title,
        description=description,
        placeholder=placeholder,
        ge=min,
        le=max,
        format_type=format_type,
        default=default,
        default_generator_type=default_generator_type,
        show_if=show_if,
        disable_if=disable_if,
        min=min,
        max=max,
        step=step,
        **kwargs,
    )


def PercentageSliderField(
    title: str,
    description: str,
    alias: Optional[str] = None,
    placeholder: str = "",
    min: float = 0,
    max: float = 1.0,
    step: float = 0.05,
    default: Optional[float] = None,
    default_generator_type: Optional[GeneratorType] = None,
    show_if: Optional[FieldConditionals] = None,
    disable_if: Optional[FieldConditionals] = None,
    **kwargs,
):
    return SliderField(
        alias=alias,
        title=title,
        description=description,
        placeholder=placeholder,
        format_type=FormatType.PERCENTAGE,
        default=default,
        default_generator_type=default_generator_type,
        show_if=show_if,
        disable_if=disable_if,
        min=min,
        max=max,
        step=step,
        **kwargs,
    )


def CheckboxField(
    title: str,
    description: str,
    alias: Optional[str] = None,
    placeholder: str = "",
    default: bool = False,
    show_if: Optional[FieldConditionals] = None,
    disable_if: Optional[FieldConditionals] = None,
    **kwargs,
):
    return BaseField(
        alias=alias,
        type=FieldType.CHECKBOX,
        title=title,
        description=description,
        placeholder=placeholder,
        default=default,
        show_if=show_if,
        disable_if=disable_if,
        **kwargs,
    )


def ColorField(
    title: str,
    description: str,
    alias: Optional[str] = None,
    placeholder: str = "",
    show_if: Optional[FieldConditionals] = None,
    disable_if: Optional[FieldConditionals] = None,
    default: Optional[str] = None,
    default_generator_type: Optional[GeneratorType] = None,
    **kwargs,
):
    return BaseField(
        alias=alias,
        type=FieldType.COLOR,
        title=title,
        description=description,
        placeholder=placeholder,
        show_if=show_if,
        disable_if=disable_if,
        default=default,
        default_generator_type=default_generator_type,
        **kwargs,
    )


def SelectField(
    title: str,
    description: str,
    options: List[Option],
    alias: Optional[str] = None,
    placeholder: str = "",
    default: Optional[SelectFieldValue] = None,
    default_generator_type: Optional[GeneratorType] = None,
    show_if: Optional[FieldConditionals] = None,
    disable_if: Optional[FieldConditionals] = None,
    multiple: bool = False,
    **kwargs,
):
    return BaseField(
        alias=alias,
        type=FieldType.SELECT,
        title=title,
        description=description,
        placeholder=placeholder,
        options=options,
        default=default,
        default_generator_type=default_generator_type,
        show_if=show_if,
        disable_if=disable_if,
        multiple=multiple,
        **kwargs,
    )


def RadioField(
    title: str,
    description: str,
    options: List[Option],
    alias: Optional[str] = None,
    placeholder: str = "",
    default: Optional[str] = None,
    default_generator_type: Optional[GeneratorType] = None,
    show_if: Optional[FieldConditionals] = None,
    disable_if: Optional[FieldConditionals] = None,
    **kwargs,
):
    return BaseField(
        alias=alias,
        type=FieldType.RADIO,
        title=title,
        description=description,
        placeholder=placeholder,
        options=options,
        default=default,
        default_generator_type=default_generator_type,
        show_if=show_if,
        disable_if=disable_if,
        **kwargs,
    )
