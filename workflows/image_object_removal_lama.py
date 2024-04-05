from typing import List
from rossa import (
    BaseWorkflow,
    ControlsField,
    Image,
    InputImageControl,
    ControlValue,
    MaskImageControl,
)


image = Image.debian_slim(python_version="3.10").pip_install(
    "simple-lama-inpainting==0.1.2"
)


with image.imports():
    from simple_lama_inpainting import SimpleLama


class Workflow(BaseWorkflow):
    image = image
    title = "Remove Objects"
    version = "Lama V1"
    description = "Seamlessly remove unwanted objects or people from images."
    tooltip = "Select the areas you want to remove, and our AI will intelligently fill those regions to blend naturally with the surrounding image."

    def download(self):
        SimpleLama()

    def load(self):
        self.simple_lama = SimpleLama()

    def run(
        self,
        controls: List[ControlValue] = ControlsField(
            options=[InputImageControl(required=True), MaskImageControl(required=True)]
        ),
    ):
        mask: ControlValue = next(
            filter(lambda control: control.type == MaskImageControl().type, controls),
            None,
        )

        image: ControlValue = next(
            filter(lambda control: control.type == InputImageControl().type, controls),
            None,
        )

        if mask is None or image is None:
            raise Exception("Mask and image are required")

        mask = mask.to_pil_image()

        image = image.to_pil_image()

        if mask is None:
            raise Exception("Mask is required. Error converting mask to Image")

        if image is None:
            raise Exception("Image is required. Error converting image to Image")

        result = self.simple_lama(image, mask)

        return result
