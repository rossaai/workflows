import argparse
import importlib
import inspect
import os
import tempfile

from .workflow import BaseWorkflow


SUPPORTED_PROVIDERS = ["modal"]

SUPPORTED_COMMANDS = ["build", "run"]

SUPPORTED_MODAL_GPUS = ["T4", "L4", "A100", "A10G", "H100"]


def create_modal_file(
    code: str,
    stub_name: str,
    gpu: str,
    force_build: bool = False,
):

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as temp_file:
        temp_file.write(code)
        temp_file_path = temp_file.name

    # Save the original environment
    prev_os_env = os.environ.copy()
    os.environ.clear()

    spec = importlib.util.spec_from_file_location("temp_module", temp_file_path)
    temp_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(temp_module)

    # Restore the original environment
    os.environ.update(prev_os_env)

    workflow_class = None
    for name, obj in inspect.getmembers(temp_module):
        if (
            inspect.isclass(obj)
            and issubclass(obj, BaseWorkflow)
            and name != "BaseWorkflow"
        ):
            workflow_class = obj
            break

    if workflow_class:
        workflow_instance = workflow_class()  # type: BaseWorkflow

        temp_dir = tempfile.mkdtemp()

        dockerfile_path = os.path.join(temp_dir, "Dockerfile")
        code_path = os.path.join(temp_dir, "deployment.py")

        code = workflow_instance.to_modal(
            modal_stub_name=stub_name,
            modal_stub_args=f"gpu=modal.gpu.{gpu}()" if gpu else "",
            custom_class_code=code,
            dockerfile_path=dockerfile_path,
            return_code_and_dockerfile=True,
            force_build=force_build,
        )

        files = [
            {"path": dockerfile_path, "content": code["dockerfile"]},
            {"path": code_path, "content": code["code"], "primary": True},
        ]

        old_dir = os.getcwd()
        temp_dir = tempfile.mkdtemp()

        os.chdir(temp_dir)

        for file in files:
            with open(file["path"], "w") as f:
                f.write(file["content"])

        os.chdir(old_dir)

        primary_file = next(file for file in files if file.get("primary", False))

        if primary_file is None:
            raise Exception("Primary file not found")

        primary_file_path = os.path.join(temp_dir, primary_file["path"])

        return primary_file_path

    else:
        raise Exception("No workflow class found in the provided code")


def main():
    parser = argparse.ArgumentParser(description="Description of your program")
    parser.add_argument(
        "provider", choices=SUPPORTED_PROVIDERS, help="The provider to use"
    )
    parser.add_argument(
        "command", choices=SUPPORTED_COMMANDS, help="The command to execute"
    )
    parser.add_argument("filepath", type=str, help="The path to the file")

    # Optional arguments for 'modal run'
    parser.add_argument("--stub", type=str, help="Use stub name")

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

    args = parser.parse_args()

    if args.provider == "modal":
        if args.command == "run":
            run_modal(args.filepath, args.stub, args.gpu, args.force_build)
        elif args.command == "build":
            build_modal(args.filepath, args.stub, args.gpu, args.force_build)
    else:
        parser.print_help()


def run_modal(filepath: str, stub_name: str, gpu: str, force_build: bool):
    # Logic to execute the "run" command for modal
    with open(filepath, "r") as f:
        code = f.read()

    modal_file = create_modal_file(code, stub_name, gpu)

    print(f"Running modal with file: {modal_file}")

    os.system(f"modal run {modal_file}")


def build_modal(filepath: str, stub_name: str, gpu: str, force_build: bool):
    with open(filepath, "r") as f:
        code = f.read()

    modal_file = create_modal_file(code, stub_name, gpu, force_build)

    print(f"Building modal with file: {modal_file}")

    os.system(f"modal build {modal_file}")


if __name__ == "__main__":
    main()
