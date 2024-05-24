import inspect
import json
from typing import Optional
from ..workflow_blueprint import WorkflowBlueprint
from .adapter import AbstractWorkflowAdapter
from ..format_utils import clean_and_format_string


class LocalWorkflowAdapter(AbstractWorkflowAdapter):
    def convert_workflow(
        self,
        workflow: WorkflowBlueprint,
        custom_class_code: Optional[str] = None,
    ):
        if custom_class_code is None:
            with open(inspect.getsourcefile(workflow.__class__), "r") as f:
                class_code = f.read()
        else:
            class_code = custom_class_code

        imports = f"""
import inspect

workflow_instance = {workflow.__class__.__name__}()\n"""

        run_method = """
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

def run_workflow_examples():
    examples = {json.dumps(formatted_examples)}
    
    folder = tempfile.mkdtemp()
    
    for example in examples:
        folder_path = os.path.join(folder, example["title"])
        os.makedirs(folder_path, exist_ok=True)
        
        results = LocalWorkflow().run(**example["data"])

        for result in results:
            if isinstance(result, Response):
                file_name = uuid.uuid4().hex
                path = os.path.join(folder_path, file_name)
                path = os.path.abspath(path)
                result.save(path)
                print("Saved (" + result.content_type + "): file://" + path)
            elif isinstance(result, Notification):
                print(result.dict())

run_workflow_examples()
"""

        deployment_code = f"""{class_code}
{imports}

class LocalWorkflow:
{run_method}
{local_examples}
"""

        return deployment_code
