import argparse
import importlib.util
import inspect
import os
import subprocess
import io
import sys
from typing import Dict, Any, Optional, List, Type

from .workflow import BaseWorkflow

SUPPORTED_PROVIDERS: List[str] = ["modal", "local"]
SUPPORTED_COMMANDS: List[str] = ["build", "run"]
SUPPORTED_MODAL_GPUS: List[str] = ["T4", "L4", "A100", "A10G", "H100"]


class InMemoryFile:
    def __init__(self, content: str):
        self.file: io.StringIO = io.StringIO(content)
        self.name: str = "in_memory_file.py"

    def __enter__(self) -> "InMemoryFile":
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any],
    ) -> None:
        self.file.close()

    def read(self) -> str:
        return self.file.getvalue()


def get_workflow_class(filepath: str) -> Type[BaseWorkflow]:
    # Get the absolute path
    abs_path = os.path.abspath(filepath)

    # Get the directory containing the file
    dir_path = os.path.dirname(abs_path)

    # Add the directory to sys.path temporarily
    sys.path.insert(0, dir_path)

    try:
        # Generate a module name from the file path
        module_name = os.path.splitext(os.path.basename(filepath))[0]

        # Import the module
        spec = importlib.util.spec_from_file_location(module_name, abs_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Find the workflow class
        for name, obj in inspect.getmembers(module):
            if (
                inspect.isclass(obj)
                and issubclass(obj, BaseWorkflow)
                and obj != BaseWorkflow
            ):
                return obj

        raise Exception("No workflow class found in the provided file")

    finally:
        # Remove the directory from sys.path
        sys.path.pop(0)


def create_modal_file(
    filepath: str,
    app_name: str,
    gpu: Optional[str],
    force_build: bool = False,
) -> InMemoryFile:
    workflow_class = get_workflow_class(filepath)
    workflow_instance: BaseWorkflow = workflow_class()

    modal_code: Dict[str, str] = workflow_instance.to_modal(
        modal_app_name=app_name,
        modal_app_args=f"gpu=modal.gpu.{gpu}()" if gpu else "",
        include_class_code=False,
        dockerfile_path="Dockerfile",
        return_code_and_dockerfile=True,
        force_build=force_build,
    )

    return InMemoryFile(modal_code["code"])


def create_local_file(filepath: str) -> InMemoryFile:
    workflow_class = get_workflow_class(filepath)
    workflow_instance: BaseWorkflow = workflow_class()

    local_code: str = workflow_instance.to_local(include_class_code=False)

    return InMemoryFile(local_code)


def main() -> None:
    parser = argparse.ArgumentParser(description="Description of your program")
    parser.add_argument(
        "provider", choices=SUPPORTED_PROVIDERS, help="The provider to use"
    )
    parser.add_argument(
        "command", choices=SUPPORTED_COMMANDS, help="The command to execute"
    )
    parser.add_argument("filepath", type=str, help="The path to the file")

    parser.add_argument("--app-name", type=str, help="Use app name")

    parser.add_argument(
        "--gpu",
        choices=SUPPORTED_MODAL_GPUS,
        default="A10G",
        help="Specify the GPU to use",
    )

    parser.add_argument(
        "--force-build",
        action="store_true",
        help="Force the build of the docker image",
    )

    args: argparse.Namespace
    args, _ = parser.parse_known_args()

    os.environ["PROVIDER"] = args.provider

    if args.provider == "modal":
        os.environ["IS_MODAL"] = "true"
        if args.command == "run":
            run_modal(args.filepath, args.app_name, args.gpu, args.force_build)
        elif args.command == "build":
            build_modal(args.filepath, args.app_name, args.gpu, args.force_build)
    elif args.provider == "local":
        os.environ["IS_LOCAL"] = "true"
        if args.command == "run":
            run_local(args.filepath)
        else:
            parser.print_help()
    else:
        parser.print_help()


def run_local(filepath: str) -> None:
    local_file: InMemoryFile = create_local_file(filepath)

    cwd = os.path.dirname(os.path.abspath(filepath))

    with local_file as f:
        subprocess.run(["python", "-c", f.read()], env=os.environ, cwd=cwd)


def run_modal(
    filepath: str, app_name: Optional[str], gpu: Optional[str], force_build: bool
) -> None:
    modal_file: InMemoryFile = create_modal_file(filepath, app_name, gpu, force_build)

    print(f"Running modal with in-memory file")

    with modal_file as f:
        subprocess.run(["modal", "run", "-"], input=f.read(), text=True, env=os.environ)


def build_modal(
    filepath: str, app_name: Optional[str], gpu: Optional[str], force_build: bool
) -> None:
    modal_file: InMemoryFile = create_modal_file(filepath, app_name, gpu, force_build)

    print(f"Building modal with in-memory file")

    with modal_file as f:
        subprocess.run(
            ["modal", "build", "-"], input=f.read(), text=True, env=os.environ
        )


if __name__ == "__main__":
    main()
