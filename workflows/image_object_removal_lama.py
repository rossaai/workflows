from typing import List
from rossa import (
    ApplicableForRequirements,
    BaseWorkflow,
    ControlRequirements,
    ControlsField,
    Image,
    InputImageControl,
    ControlValue,
    MaskImageControl,
    ImageResponse,
    next_control,
)


image = (
    Image.debian_slim(python_version="3.10")
    .apt_install("ffmpeg", "libsm6", "libxext6")
    .pip_install("simple-lama-inpainting==0.1.2")
)


with image.imports():
    from simple_lama_inpainting import SimpleLama


class Workflow(BaseWorkflow):
    image = image
    title = "Object Remover"
    version = "Lama V1"
    description = "Easily erase unwanted objects or people from your photos."

    examples = [
        {
            "title": "Remove Bench from Photo",
            "description": "This example shows how to remove a bench from a scene.",
            "data": {
                "controls": [
                    {
                        "content_type": "image",
                        "control_type": "input",
                        "influence": 1.0,
                        "content": "https://raw.githubusercontent.com/rossaai/workflows/main/assets/images/chair.png",
                    },
                    {
                        "content_type": "image",
                        "control_type": "mask",
                        "influence": 1.0,
                        "content": "https://raw.githubusercontent.com/rossaai/workflows/main/assets/images/chair_mask.png",
                    },
                ],
            },
        },
    ]

    def download(self):
        self.simple_lama = SimpleLama()

    def load(self):
        self.simple_lama = SimpleLama()

    def run(
        self,
        controls: List[ControlValue] = ControlsField(
            options=[
                InputImageControl(
                    requirements=ControlRequirements(
                        all=ApplicableForRequirements(required=True),
                    ),
                ),
                MaskImageControl(
                    requirements=ControlRequirements(
                        all=ApplicableForRequirements(required=True),
                    ),
                ),
            ]
        ),
    ):
        image = next_control(controls, InputImageControl())

        mask = next_control(controls, MaskImageControl())

        image = image.to_pil_image().convert("RGB")

        mask = mask.to_pil_image().convert("L")

        result = self.simple_lama(image, mask)

        yield ImageResponse(content=result)
