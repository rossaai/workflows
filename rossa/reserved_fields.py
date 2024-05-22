# RESERVED FIELDS
from typing import List
from .controls import BaseControl
from .fields import BaseField
from .performances import BasePerformance
from .types import FieldType


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