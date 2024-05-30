from typing import List
from rossa import (
    BaseWorkflow,
    ControlValue,
    ControlsField,
    ReferenceImageControl,
    MaskImageControl,
    next_control,
)


class Workflow(BaseWorkflow):
    def run(
        self,
        controls: List[ControlValue] = ControlsField(
            options=[ReferenceImageControl(), MaskImageControl()]
        ),
    ):
        assert len(controls) == 2, "Please provide an input image and a mask."

        assert all(
            isinstance(control, ControlValue) for control in controls
        ), "Controls must be of type ControlValue. Probably validate_arguments is not working."

        image = next_control(controls, ReferenceImageControl())

        mask = next_control(controls, MaskImageControl())

        print("Successfully extracted controls from workflow.")


workflow = Workflow()

controls = [
    {
        "content_type": "image",
        "control_type": "input",
        "influence": 1.0,
        "content": "https://picsum.photos/200",
    },
    {
        "content_type": "image",
        "control_type": "mask",
        "influence": 1.0,
        "content": "https://picsum.photos/200",
    },
]


workflow.run(
    controls=controls,
    prompt="Please provide an input image and a mask.",  # Validate if extra kwargs are allowed
)
