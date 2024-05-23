from typing import Any, Dict, List, Union

from .workflow_blueprint import WorkflowBlueprint


from .format_utils import clean_and_format_string

from .adapters.local import LocalWorkflowAdapter
from .adapters.modal import ModalWorkflowAdapter

from .responses import Notification, Response


ReturnResults = Union[
    Union[Response, Notification],
    List[Union[Response, Notification]],
]


class BaseWorkflow(WorkflowBlueprint):

    def to_modal(
        self,
        modal_app_name: str = None,
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

            deployment_code = Workflow().to_modal(
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

        # It uses the class name as the default app name instead of `self.schema()["title"]` due to Modal naming constraints.
        modal_app_name = modal_app_name or clean_and_format_string(
            self.schema()["title"]
        )

        adapter = ModalWorkflowAdapter()

        return adapter.convert_workflow(
            self,
            modal_app_name,
            modal_app_args,
            custom_class_code,
            dockerfile_path,
            force_build,
            return_code_and_dockerfile,
        )

    def to_local(
        self,
        custom_class_code: str = None,
    ) -> str:
        adapter = LocalWorkflowAdapter()

        return adapter.convert_workflow(self, custom_class_code=custom_class_code)
