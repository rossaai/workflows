from typing import List, Union

from .reserved_fields import ControlOption

from .reserved_field_values import ControlValue

from .types import ControlType

from .exceptions import ControlNotFoundException


def next_control(
    controls: List[ControlValue], control: Union[ControlOption, ControlType, str]
) -> ControlValue:
    control_type = control.value if isinstance(control, ControlOption) else control

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
