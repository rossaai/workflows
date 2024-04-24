from typing import List
from rossa import (
    BaseWorkflow,
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

    def download(self):
        self.simple_lama = SimpleLama()

    def load(self):
        self.simple_lama = SimpleLama()

    def run(
        self,
        controls: List[ControlValue] = ControlsField(
            options=[InputImageControl(), MaskImageControl()]
        ),
    ):
        mask = next_control(controls, MaskImageControl())

        image = next_control(controls, InputImageControl())

        mask = mask.to_pil_image()

        image = image.to_pil_image()

        result = self.simple_lama(image, mask)

        yield ImageResponse(content=result)
