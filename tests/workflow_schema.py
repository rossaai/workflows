from workflows.image_object_removal_lama import Workflow

workflow = Workflow()


schema = workflow.schema()


assert (
    len(schema["fields"]) > 0
), "Schema fields should not be empty. Check if run method has ControlsField or BaseWorkflow is extracting the cls.run's parameters correctly."

print(schema)
