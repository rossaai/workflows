from typing import List, Union

from .types import ControlType

from .exceptions import ControlNotFoundException
from .controls import BaseControl, ControlValue


def next_control(
    controls: List[ControlValue], control: Union[BaseControl, ControlType, str]
) -> ControlValue:
    control_type = control.value if isinstance(control, BaseControl) else control

    value = next(
        filter(
            lambda c: (c.control_type == control_type),
            controls,
        ),
        None,
    )

    if value is None:
        raise ControlNotFoundException(
            f"{control.title} ({control.value}) control is required. Available controls: {[c.control_type for c in controls]}"
        )

    return value
