from .image import Image
from .schema import FieldType
from abc import abstractmethod
from pydantic import BaseModel, validate_arguments
from pydantic.fields import FieldInfo
import inspect


class BaseWorkflow(BaseModel):
    def __init_subclass__(cls, image: Image, version: str, **kwargs):
        cls.version = version
        cls.image = image
        super().__init_subclass__(**kwargs)
        cls.run = validate_arguments(cls.run)

    def schema(self):
        super_schema = super().schema()

        fields = []

        for name, param in inspect.signature(self.run).parameters.items():
            default = param.default

            is_not_valid_field = (
                default == inspect.Parameter.empty
                or not isinstance(default, FieldInfo)
                or "type" not in default.extra
                and default.extra["type"] not in set(FieldType)
            )

            if is_not_valid_field:
                continue

            options = []

            # validate if .options is a list and is in default.extra class
            if "options" in default.extra and isinstance(
                default.extra["options"], list
            ):
                for option in default.extra["options"]:
                    options.append(option.dict())

            fields.append(
                {
                    "key": name,
                    "title": default.title,
                    "type": default.extra["type"],
                    "description": default.description,
                    "options": options,
                }
            )

        new_schema = {
            "title": super_schema["title"],
            "description": super_schema["description"],
            "version": self.version,
            "fields": fields,
        }

        return new_schema

    @property
    def image(self) -> Image:
        return self.image

    def download(self):
        pass

    def load(self):
        pass

    @abstractmethod
    def run(self):
        pass

    def to_modal(
        self,
        stub_name: str = None,
        stub_args: str = "",
        cls_code: str = None,
        return_dict: bool = False,
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

        dockerfile = self.image.to_dockerfile()

        stub_name = stub_name or self.schema()["title"]

        dockerfilename = "Dockerfile"

        if not return_dict:
            import tempfile

            dockerfilename = tempfile.mktemp()

            with open(dockerfilename, "w") as f:
                f.write(dockerfile)

        if cls_code is None:
            with open(inspect.getsourcefile(self.__class__), "r") as f:
                code = f.read()
        else:
            code = cls_code

        code = f"""
{code}

import modal

modal_image = modal.Image.from_dockerfile({dockerfilename!r})

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

        if return_dict:
            return {
                "code": code,
                "dockerfile": dockerfile,
                "dockerfilename": dockerfilename,
            }

        return code
