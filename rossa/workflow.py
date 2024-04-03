from .image import Image
from abc import abstractmethod
from pydantic import BaseModel, validate_arguments
import inspect
from fastapi import Response


class BaseWorkflow(BaseModel):
    def __init_subclass__(cls, image: Image, **kwargs):
        cls.image = image
        super().__init_subclass__(**kwargs)
        cls.run = validate_arguments(cls.run)

    @property
    def image(self) -> Image:
        return self.image

    def download(self):
        pass

    def load(self):
        pass

    @abstractmethod
    def run(self) -> Response:
        pass

    def to_modal(
        self,
        stub_name: str = None,
        stub_args: str = "",
    ) -> str:
        """
        Returns a script or file content as a string to deploy the workflow on Modal's cloud infrastructure.

        This method generates the necessary code or file content to deploy your workflow on Modal.
        It takes several arguments to configure the deployment settings.

        Args:
            stub_name (str): The name of the workflow stub.
            stub_args (str, optional): Additional arguments to pass to the workflow stub.

        NOTE: Every modal import should be imported by `modal.*` such as `modal.gpu.A10G()` or `modal.Secret.from_name("super-secret")`

        Example:
            ```python
            import modal
            import os

            deployment_script = Workflow().to_modal(
                stub_name="image-to-threed-triposr",
                stub_args=\"""
                gpu=modal.gpu.A10G(),
                allow_concurrent_inputs=4,
                container_idle_timeout=240,
                secrets=[modal.Secret.from_name("super-secret")]\""",
            )

            with open("deployment.py", "w") as f:
                f.write(deployment_script)

            os.system("modal deploy deployment.py")
        ```"""
        import tempfile

        dockerfile = self.image.to_dockerfile()

        stub_name = stub_name or self.schema()["title"]

        tempfilename = tempfile.mktemp()

        with open(tempfilename, "w") as f:
            f.write(dockerfile)

        with open(inspect.getsourcefile(self.__class__), "r") as f:
            code = f.read()

        code = f"""
{code}

import modal

modal_image = modal.Image.from_dockerfile({tempfilename!r})

stub = modal.Stub({stub_name!r})

workflow_to_modal = {self.__class__.__name__}()

@stub.cls(
    image=modal_image,
    {stub_args}
)
class ModalWorkflow:
    @modal.build()
    def download(self, *args, **kwargs):
        return workflow_to_modal.download(*args, **kwargs)

    @modal.enter()
    def load(self, *args, **kwargs):
        return workflow_to_modal.load(*args, **kwargs)

    @modal.method()
    def run(self, *args, **kwargs):
        return workflow_to_modal.run(*args, **kwargs)
"""

        return code
