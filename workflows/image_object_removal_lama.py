from typing import List
from rossa import (
    BaseWorkflow,
    ControlsField,
    Image,
    InputImageControl,
    ControlValue,
    MaskImageControl,
    ContentType,
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
    title = "Remove Objects"
    version = "Lama V1"
    description = "Seamlessly remove unwanted objects or people from images."
    tooltip = "Select the areas you want to remove, and our AI will intelligently fill those regions to blend naturally with the surrounding image."
    content_type = ContentType.IMAGE

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
