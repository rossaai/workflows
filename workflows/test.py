import inspect
import traceback
from typing import List

import modal.gpu
from rossa import (
    BaseWorkflow,
    ControlsField,
    Image,
    InputImageControl,
    ControlValue,
    MaskImageControl,
    ContentType,
    ImageResponse,
    Response,
    ErrorNotification,
    Notification,
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
            options=[InputImageControl(required=True), MaskImageControl(required=True)]
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


import modal

modal_image = modal.Image.from_dockerfile(
    "/var/folders/x7/19qwc2yx24b3f16020mbpx7h0000gn/T/tmpom_0tl7k", force_build=False
).pip_install("git+https://github.com/rossaai/workflows", force_build=False)

stub = modal.Stub("Workflow")

workflow_instance = Workflow()

workflow_instance.schema()


@stub.cls(image=modal_image, gpu=modal.gpu.A10G())
class ModalWorkflow:
    @modal.build()
    def download(self):
        return workflow_instance.download()

    @modal.enter()
    def load(self):
        return workflow_instance.load()

    @modal.method()
    def run(self, *args, **kwargs):
        try:
            result = workflow_instance.run(*args, **kwargs)

            if inspect.isgenerator(result):
                for x in result:
                    yield x
            else:
                yield result
        except Exception as e:
            tb = traceback.format_exc()
            yield ErrorNotification(
                title="Error",
                message=str(e),
                traceback=tb,
            )


@stub.local_entrypoint()
def run_workflow():
    def path_to_base64_with_header(path):
        import base64

        with open(path, "rb") as image_file:
            return (
                f"data:image/jpeg;base64,{base64.b64encode(image_file.read()).decode()}"
            )

    results = ModalWorkflow.run.remote_gen(
        **{
            "controls": [
                {
                    "type": "input",
                    "influence": 1.0,
                    "url": path_to_base64_with_header(
                        "/Users/felipemurguia/git-clone/workflow-api/images/chair.png"
                    ),
                },
                {
                    "type": "mask",
                    "influence": 1.0,
                    "url": path_to_base64_with_header(
                        "/Users/felipemurguia/git-clone/workflow-api/images/chair_mask.png"
                    ),
                },
            ]
        }
    )

    for result in results:
        if isinstance(result, Response):
            result.save("/Users/felipemurguia/git-clone/workflow-api/images/output.png")
        elif isinstance(result, Notification):
            print(result.dict())
