from typing import List
from rossa import (
    BaseWorkflow,
    ControlsField,
    Image,
    InputImageControl,
    ControlValue,
    MaskImageControl,
    ImageResponse,
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
        mask: ControlValue = next(
            filter(lambda control: control.type == MaskImageControl().value, controls),
            None,
        )

        image: ControlValue = next(
            filter(lambda control: control.type == InputImageControl().value, controls),
            None,
        )

        if mask is None or image is None:
            raise Exception("Control mask and image are required.")

        mask = mask.to_pil_image()

        image = image.to_pil_image()

        result = self.simple_lama(image, mask)

        yield ImageResponse(content=result)
