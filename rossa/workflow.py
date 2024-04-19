from typing import Any, Dict, Optional, Union
from .image import Image
from .fields import FieldType, Option
from abc import abstractmethod
from .types import ContentType
from pydantic import validate_arguments
from pydantic.fields import FieldInfo
import inspect


class BaseWorkflow:
    image: Optional[Image] = None
    title: str
    version: str
    description: str
    content_type: ContentType
    tooltip: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.run = validate_arguments(cls.run)

    def schema(self):
        # validate title, version, description, content_type, and tooltip
        if not isinstance(self.title, str):
            raise ValueError("title must be a string")
        if not isinstance(self.version, str):
            raise ValueError("version must be a string")
        if not isinstance(self.description, str):
            raise ValueError("description must be a string")
        if not isinstance(self.content_type, ContentType):
            raise ValueError("content_type must be a ContentType")

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
                    if isinstance(option, Option):
                        options.append(option.dict())

            fields.append(
                {
                    "name": name,
                    "title": default.title,
                    "type": default.extra["type"],
                    "description": default.description,
                    "options": options,
                }
            )

        new_schema = {
            "title": self.title,
            "version": self.version,
            "description": self.description,
            "content_type": self.content_type.value,
            "tooltip": self.tooltip or "",
            "fields": fields,
        }

        return new_schema

    def download(self):
        pass

    def load(self):
        pass

    @abstractmethod
    def run(self):
        pass

    def to_modal(
        self,
        modal_stub_name: str = None,
        modal_stub_args: str = "",
        custom_class_code: str = None,
        dockerfile_path: str = None,
        force_build: bool = False,
        return_code_and_dockerfile: bool = False,
    ) -> Union[str, Dict[str, Any]]:
        """
        Generates the necessary code or file content to deploy the workflow on Modal's cloud infrastructure.

        This method creates a script that can be used to deploy your workflow on Modal. It takes several
        arguments to customize the deployment settings, such as the stub name, additional stub arguments,
        and custom class code.

        Args:
            modal_stub_name (str): The name of the Modal stub for the workflow.
            modal_stub_args (str, optional): Additional arguments to pass to the Modal stub.
            custom_class_code (str, optional): Custom class code to include in the generated script.
            dockerfile_path (str, optional): Path to save the generated Dockerfile. If not provided, a temporary file will be used.
            return_code_and_dockerfile (bool, optional): Whether to return the generated code and Dockerfile content as a dictionary.

        Returns:
            str or Dict[str, Any]: The generated Modal deployment code, or a dictionary containing the code and Dockerfile content.

        NOTE: Every Modal import should be imported using `modal.*`, such as `modal.gpu.A10G()` or `modal.Secret.from_name("super-secret")`.

        Example:
            ```python
            import modal
            import os

            deployment_code = Workflow().generate_modal_deployment_code(
                modal_stub_name="image-to-threed-triposr",
                modal_stub_args=\"""
                gpu=modal.gpu.A10G(),
                allow_concurrent_inputs=4,
                container_idle_timeout=240,
                secrets=[modal.Secret.from_name("super-secret")]\""",
            )

            with open("deployment.py", "w") as f:
                f.write(deployment_code)

            os.system("modal deploy deployment.py")
        ```
        """

        # It uses the class name as the default stub name instead of `self.schema()["title"]` due to Modal naming constraints.
        modal_stub_name = modal_stub_name or self.__class__.__name__[:64]
        dockerfile_path = dockerfile_path or "Dockerfile"

        if self.image:
            dockerfile_content = self.image.to_dockerfile()

            if not return_code_and_dockerfile:
                import tempfile

                dockerfile_path = tempfile.mktemp()
                with open(dockerfile_path, "w") as f:
                    f.write(dockerfile_content)

        if custom_class_code is None:
            with open(inspect.getsourcefile(self.__class__), "r") as f:
                class_code = f.read()
        else:
            class_code = custom_class_code

        is_same_download_method = inspect.getsource(self.download) == inspect.getsource(
            BaseWorkflow.download
        )
        is_same_load_method = inspect.getsource(self.load) == inspect.getsource(
            BaseWorkflow.load
        )

        if self.image:
            modal_import = f"""
import modal

modal_image = modal.Image.from_dockerfile(
    {dockerfile_path!r}, 
    force_build={force_build}
)
    
stub = modal.Stub({modal_stub_name!r})

workflow_instance = {self.__class__.__name__}()\n"""
        else:
            modal_import = f"""import modal\n\nstub = modal.Stub({modal_stub_name!r})\n\nworkflow_instance = {self.__class__.__name__}()\n"""

        download_method = ""

        stub_args = "image=modal_image" if self.image else ""

        if self.image and modal_stub_args:
            stub_args += ",\n"

        stub_args += modal_stub_args if modal_stub_args else ""

        if not is_same_download_method:
            download_method = """
    @modal.build()
    def download(self):
        return workflow_instance.download()
"""

        load_method = ""
        if not is_same_load_method:
            load_method = """
    @modal.enter()
    def load(self):
        return workflow_instance.load()
"""

        run_method = """
    @modal.method()
    def run(self, *args, **kwargs):
        return workflow_instance.run(*args, **kwargs)
"""

        deployment_code = f"""{class_code}
{modal_import}

@stub.cls(
    {stub_args}
)
class ModalWorkflow:
{download_method}
{load_method}
{run_method}
"""

        if return_code_and_dockerfile:
            return {
                "code": deployment_code,
                "dockerfile": dockerfile_content,
                "dockerfile_path": dockerfile_path,
            }

        return deployment_code
