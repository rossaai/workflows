import json
from typing import Any, Dict, Union
import inspect

from .adapter import AbstractWorkflowAdapter
from ..image import Image
from ..workflow_blueprint import WorkflowBlueprint
from ..format_utils import clean_and_format_string


class ModalWorkflowAdapter(AbstractWorkflowAdapter):
    def convert_workflow(
        self,
        workflow: WorkflowBlueprint,
        modal_app_name: str,
        modal_app_args: str = "",
        custom_class_code: str = None,
        dockerfile_path: str = None,
        force_build: bool = False,
        return_code_and_dockerfile: bool = False,
    ) -> Union[str, Dict[str, Any]]:
        """
        Generates the necessary code or file content to deploy the workflow on Modal's cloud infrastructure.

        This method creates a script that can be used to deploy your workflow on Modal. It takes several
        arguments to customize the deployment settings, such as the app name, additional app arguments,
        and custom class code.

        Args:
            modal_app_name (str): The name of the Modal app for the workflow.
            modal_app_args (str, optional): Additional arguments to pass to the Modal app.
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
                modal_app_name="image-to-threed-triposr",
                modal_app_args=\"""
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

        # It uses the class name as the default app name instead of `workflow.schema()["title"]` due to Modal naming constraints.
        dockerfile_path = dockerfile_path or "Dockerfile"

        if isinstance(workflow.image, Image):
            dockerfile_content = workflow.image.to_dockerfile()

            if not return_code_and_dockerfile:
                import tempfile

                dockerfile_path = tempfile.mktemp()
                with open(dockerfile_path, "w") as f:
                    f.write(dockerfile_content)

        if custom_class_code is None:
            with open(inspect.getsourcefile(workflow.__class__), "r") as f:
                class_code = f.read()
        else:
            class_code = custom_class_code

        is_same_download_method = inspect.getsource(
            workflow.download
        ) == inspect.getsource(WorkflowBlueprint.download)
        is_same_load_method = inspect.getsource(workflow.load) == inspect.getsource(
            WorkflowBlueprint.load
        )

        if isinstance(workflow.image, Image):
            imports = f"""
import modal
import inspect

modal_image = modal.Image.from_dockerfile(
    {dockerfile_path!r}, 
    force_build={force_build}
)
    
app = modal.App({modal_app_name!r})

workflow_instance = {workflow.__class__.__name__}()\n"""
        else:
            imports = f"""
import modal
import inspect

workflow_instance = {workflow.__class__.__name__}()\n"""

        download_method = ""

        app_args = "image=modal_image" if workflow.image else ""

        if workflow.image and modal_app_args:
            app_args += ",\n"

        app_args += modal_app_args if modal_app_args else ""

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
    @modal.method(is_generator=True)
    def run(self, *args, **kwargs):
        result = workflow_instance.run(*args, **kwargs)

        if inspect.isgenerator(result):
            for x in result:
                yield x
        else:
            yield result
"""

        local_examples = ""

        if isinstance(workflow.examples, list):
            formatted_examples = [
                {
                    **example,
                    "title": clean_and_format_string(example["title"]),
                }
                for example in workflow.examples
            ]

            local_examples = f"""
import os
import uuid
from rossa import Response, Notification
import tempfile

@app.local_entrypoint()
def run_modal_workflow():
    examples = {json.loads(json.dumps(formatted_examples))}
    
    folder = tempfile.mkdtemp()
    
    for example in examples:
        folder_path = os.path.join(folder, example["title"])
        os.makedirs(folder_path, exist_ok=True)
        
        results = ModalWorkflow.run.remote_gen(**example["data"])

        for result in results:
            if isinstance(result, Response):
                file_name = uuid.uuid4().hex
                path = os.path.join(folder_path, file_name)
                path = os.path.abspath(path)
                result.save(path)
                print("Saved (" + result.content_type + "): " + path)
            elif isinstance(result, Notification):
                print(result.dict())

"""

        deployment_code = f"""{class_code}
{imports}

@app.cls(
    {app_args}
)
class ModalWorkflow:
{download_method}
{load_method}
{run_method}
{local_examples}
"""

        if return_code_and_dockerfile:
            return {
                "code": deployment_code,
                "dockerfile": dockerfile_content,
                "dockerfile_path": dockerfile_path,
            }

        return deployment_code
