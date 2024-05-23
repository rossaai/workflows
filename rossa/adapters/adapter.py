from abc import ABC, abstractmethod

from ..workflow_blueprint import WorkflowBlueprint


class AbstractWorkflowAdapter(ABC):
    @abstractmethod
    def convert_workflow(
        self,
        workflow: WorkflowBlueprint,
    ):
        pass
