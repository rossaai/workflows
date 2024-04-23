from typing import List
from rossa import (
    BaseWorkflow,
    ControlValue,
    ControlsField,
    InputImageControl,
    MaskImageControl,
)


class Workflow(BaseWorkflow):
    def run(
        self,
        controls: List[ControlValue] = ControlsField(
            options=[InputImageControl(), MaskImageControl()]
        ),
    ):
        assert len(controls) == 2, "Please provide an input image and a mask."

        assert all(
            isinstance(control, ControlValue) for control in controls
        ), "Controls must be of type ControlValue. Probably validate_arguments is not working."
        pass


workflow = Workflow()

controls = [
    {
        "content_type": "image",
        "type": "input",
        "influence": 1.0,
        "url": "https://example.com/image.jpg",
    },
    {
        "content_type": "image",
        "type": "mask",
        "influence": 1.0,
        "url": "https://example.com/mask.jpg",
    },
]


# Expect to
workflow.run(
    controls=controls,
)
