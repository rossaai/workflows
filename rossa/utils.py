from typing import List

from .exceptions import ControlNotFoundException
from .controls import BaseControl, ControlValue


def next_control(controls: List[ControlValue], control: BaseControl):
    value = next(
        filter(
            lambda c: (c.control_type == control.value),
            controls,
        ),
        None,
    )

    if value is None:
        raise ControlNotFoundException(
            f"{control.title} ({control.value}) control is required. Available controls: {[c.control_type for c in controls]}"
        )

    return value
