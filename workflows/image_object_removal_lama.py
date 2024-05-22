from typing import List
from rossa import (
    ContentType,
    ImageControlContent,
    MaskControlContent,
    BaseWorkflow,
    ControlsField,
    Image,
    InputImageControl,
    ControlValue,
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
                    supported_contents=[
                        ImageControlContent(),
                        MaskControlContent(),
                    ],
                ),
            ]
        ),
    ):
        image = next_control(controls, InputImageControl())

        image = image.to_pil_image(ContentType.IMAGE).convert("RGB")

        mask = image.to_pil_image(ContentType.MASK).convert("L")

        result = self.simple_lama(image, mask)

        yield ImageResponse(content=result)
