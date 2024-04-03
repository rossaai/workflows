# Copyright Modal Labs 2022
# Thanks to the authors of the original code from which this is derived:
import contextlib
import os
import shlex
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Literal, Optional, Tuple, Union
import warnings


# This is used for both type checking and runtime validation
ImageBuilderVersion = Literal["2023.12", "PREVIEW"]


def _validate_python_version(version: str) -> None:
    components = version.split(".")
    supported_versions = {"3.12", "3.11", "3.10", "3.9", "3.8"}
    if len(components) == 2 and version in supported_versions:
        return
    elif len(components) == 3:
        raise Exception(
            f"major.minor.patch version specification not valid. Supported major.minor versions are {supported_versions}."
        )
    raise Exception(
        f"Unsupported version {version}. Supported versions are {supported_versions}."
    )


def _dockerhub_python_version(python_version=None):
    if python_version is None:
        python_version = "%d.%d" % sys.version_info[:2]

    parts = python_version.split(".")

    if len(parts) > 2:
        return python_version

    # We use the same major/minor version, but the highest micro version
    # See https://hub.docker.com/_/python
    latest_micro_version = {
        "3.12": "1",
        "3.11": "0",
        "3.10": "8",
        "3.9": "15",
        "3.8": "15",
    }
    major_minor_version = ".".join(parts[:2])
    python_version = (
        major_minor_version + "." + latest_micro_version[major_minor_version]
    )
    return python_version


def _get_client_requirements_path(python_version: Optional[str] = None) -> str:
    # Locate Modal client requirements.txt
    import modal

    modal_path = modal.__path__[0]
    if python_version is None:
        major, minor, *_ = sys.version_info
    else:
        major, minor = python_version.split("-")[0].split(".")[:2]
    suffix = {(3, 12): ".312"}.get((int(major), int(minor)), "")
    return os.path.join(modal_path, f"requirements{suffix}.txt")


def _flatten_str_args(
    function_name: str, arg_name: str, args: Tuple[Union[str, List[str]], ...]
) -> List[str]:
    """Takes a tuple of strings, or string lists, and flattens it.

    Raises an error if any of the elements are not strings or string lists.
    """
    # TODO(erikbern): maybe we can just build somthing intelligent that checks
    # based on type annotations in real time?
    # Or use something like this? https://github.com/FelixTheC/strongtyping

    def is_str_list(x):
        return isinstance(x, list) and all(isinstance(y, str) for y in x)

    ret: List[str] = []
    for x in args:
        if isinstance(x, str):
            ret.append(x)
        elif is_str_list(x):
            ret.extend(x)
        else:
            raise Exception(f"{function_name}: {arg_name} must only contain strings")
    return ret


def _make_pip_install_args(
    find_links: Optional[str] = None,  # Passes -f (--find-links) pip install
    index_url: Optional[str] = None,  # Passes -i (--index-url) to pip install
    extra_index_url: Optional[str] = None,  # Passes --extra-index-url to pip install
    pre: bool = False,  # Passes --pre (allow pre-releases) to pip install
) -> str:
    flags = [
        ("--find-links", find_links),  # TODO(erikbern): allow multiple?
        ("--index-url", index_url),
        ("--extra-index-url", extra_index_url),  # TODO(erikbern): allow multiple?
    ]

    args = " ".join(
        flag + " " + shlex.quote(value) for flag, value in flags if value is not None
    )
    if pre:
        args += " --pre"

    return args


@dataclass
class DockerfileSpec:
    # Ideally we would use field() with default_factory=, but doesn't work with synchronicity type-stub gen
    commands: List[str]
    context_files: Dict[str, str]


class _Image:
    """Base class for container images to run functions in.

    Do not construct this class directly; instead use one of its static factory methods,
    such as `modal.Image.debian_slim`, `modal.Image.from_registry`, or `modal.Image.conda`.
    """

    inside_exceptions: List[Exception] = []

    def _initialize_from_empty(self):
        self.inside_exceptions = []

    commands: List[DockerfileSpec] = []

    @staticmethod
    def _from_args(
        base_images: Optional[Dict[str, "_Image"]] = None,
        dockerfile_function: Optional[
            Callable[[ImageBuilderVersion], DockerfileSpec]
        ] = None,
    ):
        if base_images is None:
            base_images = {}

        image = base_images["base"] if "base" in base_images else _Image()

        image.commands.append(dockerfile_function(ImageBuilderVersion))

        return image

    def pip_install(
        self,
        *packages: Union[
            str, List[str]
        ],  # A list of Python packages, eg. ["numpy", "matplotlib>=3.5.0"]
        find_links: Optional[str] = None,  # Passes -f (--find-links) pip install
        index_url: Optional[str] = None,  # Passes -i (--index-url) to pip install
        extra_index_url: Optional[
            str
        ] = None,  # Passes --extra-index-url to pip install
        pre: bool = False,  # Passes --pre (allow pre-releases) to pip install
    ) -> "_Image":
        """Install a list of Python packages using pip.

        **Example**

        ```python
        image = modal.Image.debian_slim().pip_install("click", "httpx~=0.23.3")
        ```
        """
        pkgs = _flatten_str_args("pip_install", "packages", packages)
        if not pkgs:
            return self

        def build_dockerfile(version: ImageBuilderVersion) -> DockerfileSpec:
            extra_args = _make_pip_install_args(
                find_links, index_url, extra_index_url, pre
            )
            package_args = " ".join(shlex.quote(pkg) for pkg in sorted(pkgs))

            commands = [
                "FROM base",
                f"RUN python -m pip install {package_args} {extra_args}",
                # TODO(erikbern): if extra_args is empty, we add a superfluous space at the end.
                # However removing it at this point would cause image hashes to change.
                # Maybe let's remove it later when/if client requirements change.
            ]
            return DockerfileSpec(commands=commands, context_files={})

        return _Image._from_args(
            base_images={"base": self},
            dockerfile_function=build_dockerfile,
        )

    def pip_install_private_repos(
        self,
        *repositories: str,
        git_user: str,
        find_links: Optional[str] = None,  # Passes -f (--find-links) pip install
        index_url: Optional[str] = None,  # Passes -i (--index-url) to pip install
        extra_index_url: Optional[
            str
        ] = None,  # Passes --extra-index-url to pip install
        pre: bool = False,  # Passes --pre (allow pre-releases) to pip install
    ) -> "_Image":
        """
        Install a list of Python packages from private git repositories using pip.

        This method currently supports Github and Gitlab only.

        - **Github:** Provide a `modal.Secret` that contains a `GITHUB_TOKEN` key-value pair
        - **Gitlab:** Provide a `modal.Secret` that contains a `GITLAB_TOKEN` key-value pair

        These API tokens should have permissions to read the list of private repositories provided as arguments.

        We recommend using Github's ['fine-grained' access tokens](https://github.blog/2022-10-18-introducing-fine-grained-personal-access-tokens-for-github/).
        These tokens are repo-scoped, and avoid granting read permission across all of a user's private repos.

        **Example**

        ```python
        image = (
            modal.Image
            .debian_slim()
            .pip_install_private_repos(
                "github.com/ecorp/private-one@1.0.0",
                "github.com/ecorp/private-two@main"
                "github.com/ecorp/private-three@d4776502"
                # install from 'inner' directory on default branch.
                "github.com/ecorp/private-four#subdirectory=inner",
                git_user="erikbern",
                secrets=[modal.Secret.from_name("github-read-private")],
            )
        )
        ```
        """

        invalid_repos = []
        install_urls = []
        for repo_ref in repositories:
            if not isinstance(repo_ref, str):
                invalid_repos.append(repo_ref)
            parts = repo_ref.split("/")
            if parts[0] == "github.com":
                install_urls.append(f"git+https://{git_user}:$GITHUB_TOKEN@{repo_ref}")
            elif parts[0] == "gitlab.com":
                install_urls.append(f"git+https://{git_user}:$GITLAB_TOKEN@{repo_ref}")
            else:
                invalid_repos.append(repo_ref)

        if invalid_repos:
            raise Exception(
                f"{len(invalid_repos)} out of {len(repositories)} given repository refs are invalid. "
                f"Invalid refs: {invalid_repos}. "
            )

        secret_names = ",".join([s.app_name if hasattr(s, "app_name") else str(s) for s in secrets])  # type: ignore

        def build_dockerfile(version: ImageBuilderVersion) -> DockerfileSpec:
            commands = ["FROM base"]
            if any(r.startswith("github") for r in repositories):
                commands.append(
                    f"RUN bash -c \"[[ -v GITHUB_TOKEN ]] || (echo 'GITHUB_TOKEN env var not set by provided modal.Secret(s): {secret_names}' && exit 1)\"",
                )
            if any(r.startswith("gitlab") for r in repositories):
                commands.append(
                    f"RUN bash -c \"[[ -v GITLAB_TOKEN ]] || (echo 'GITLAB_TOKEN env var not set by provided modal.Secret(s): {secret_names}' && exit 1)\"",
                )

            extra_args = _make_pip_install_args(
                find_links, index_url, extra_index_url, pre
            )
            commands.extend(["RUN apt-get update && apt-get install -y git"])
            commands.extend(
                [
                    f'RUN python3 -m pip install "{url}" {extra_args}'
                    for url in install_urls
                ]
            )
            return DockerfileSpec(commands=commands, context_files={})

        return _Image._from_args(
            base_images={"base": self},
            dockerfile_function=build_dockerfile,
        )

    def pip_install_from_requirements(
        self,
        requirements_txt: str,  # Path to a requirements.txt file.
        find_links: Optional[str] = None,  # Passes -f (--find-links) pip install
        *,
        index_url: Optional[str] = None,  # Passes -i (--index-url) to pip install
        extra_index_url: Optional[
            str
        ] = None,  # Passes --extra-index-url to pip install
        pre: bool = False,  # Passes --pre (allow pre-releases) to pip install
    ) -> "_Image":
        """Install a list of Python packages from a local `requirements.txt` file."""

        def build_dockerfile(version: ImageBuilderVersion) -> DockerfileSpec:
            requirements_txt_path = os.path.expanduser(requirements_txt)
            context_files = {"/.requirements.txt": requirements_txt_path}

            find_links_arg = f"-f {find_links}" if find_links else ""
            extra_args = _make_pip_install_args(
                find_links, index_url, extra_index_url, pre
            )

            commands = [
                "FROM base",
                "COPY /.requirements.txt /.requirements.txt",
                f"RUN python -m pip install -r /.requirements.txt {find_links_arg} {extra_args}",
            ]
            return DockerfileSpec(commands=commands, context_files=context_files)

        return _Image._from_args(
            base_images={"base": self},
            dockerfile_function=build_dockerfile,
        )

    def pip_install_from_pyproject(
        self,
        pyproject_toml: str,
        optional_dependencies: List[str] = [],
        *,
        find_links: Optional[str] = None,  # Passes -f (--find-links) pip install
        index_url: Optional[str] = None,  # Passes -i (--index-url) to pip install
        extra_index_url: Optional[
            str
        ] = None,  # Passes --extra-index-url to pip install
        pre: bool = False,  # Passes --pre (allow pre-releases) to pip install
    ) -> "_Image":
        """Install dependencies specified by a local `pyproject.toml` file.

        `optional_dependencies` is a list of the keys of the
        optional-dependencies section(s) of the `pyproject.toml` file
        (e.g. test, doc, experiment, etc). When provided,
        all of the packages in each listed section are installed as well.
        """

        def build_dockerfile(version: ImageBuilderVersion) -> DockerfileSpec:
            # Defer toml import so we don't need it in the container runtime environment
            import toml

            config = toml.load(os.path.expanduser(pyproject_toml))

            dependencies = []
            if "project" not in config or "dependencies" not in config["project"]:
                msg = (
                    "No [project.dependencies] section in pyproject.toml file. "
                    "If your pyproject.toml instead declares [tool.poetry.dependencies], use `Image.poetry_install_from_file()`. "
                    "See https://packaging.python.org/en/latest/guides/writing-pyproject-toml for further file format guidelines."
                )
                raise ValueError(msg)
            else:
                dependencies.extend(config["project"]["dependencies"])
            if optional_dependencies:
                optionals = config["project"]["optional-dependencies"]
                for dep_group_name in optional_dependencies:
                    if dep_group_name in optionals:
                        dependencies.extend(optionals[dep_group_name])

            extra_args = _make_pip_install_args(
                find_links, index_url, extra_index_url, pre
            )
            package_args = " ".join(shlex.quote(pkg) for pkg in sorted(dependencies))

            commands = [
                "FROM base",
                f"RUN python -m pip install {package_args} {extra_args}",
                # TODO(erikbern): if extra_args is empty, we add a superfluous space at the end.
                # However removing it at this point would cause image hashes to change.
                # Maybe let's remove it later when/if client requirements change.
            ]
            return DockerfileSpec(commands=commands, context_files={})

        return _Image._from_args(
            base_images={"base": self},
            dockerfile_function=build_dockerfile,
        )

    def poetry_install_from_file(
        self,
        poetry_pyproject_toml: str,
        # Path to the lockfile. If not provided, uses poetry.lock in the same directory.
        poetry_lockfile: Optional[str] = None,
        # If set to True, it will not use poetry.lock
        ignore_lockfile: bool = False,
        # If set to True, use old installer. See https://github.com/python-poetry/poetry/issues/3336
        old_installer: bool = False,
        # Selected optional dependency groups to install (See https://python-poetry.org/docs/cli/#install)
        with_: List[str] = [],
        # Selected optional dependency groups to exclude (See https://python-poetry.org/docs/cli/#install)
        without: List[str] = [],
        # Only install dependency groups specifed in this list.
        only: List[str] = [],
    ) -> "_Image":
        """Install poetry *dependencies* specified by a local `pyproject.toml` file.

        If not provided as argument the path to the lockfile is inferred. However, the
        file has to exist, unless `ignore_lockfile` is set to `True`.

        Note that the root project of the poetry project is not installed,
        only the dependencies. For including local packages see `modal.Mount.from_local_python_packages`
        """

        def build_dockerfile(version: ImageBuilderVersion) -> DockerfileSpec:
            context_files = {
                "/.pyproject.toml": os.path.expanduser(poetry_pyproject_toml)
            }

            commands = ["FROM base", "RUN python -m pip install poetry~=1.7"]

            if old_installer:
                commands += ["RUN poetry config experimental.new-installer false"]

            if not ignore_lockfile:
                nonlocal poetry_lockfile
                if poetry_lockfile is None:
                    p = Path(poetry_pyproject_toml).parent / "poetry.lock"
                    if not p.exists():
                        raise Exception(
                            f"poetry.lock not found at inferred location: {p.absolute()}. If a lockfile is not needed, `ignore_lockfile=True` can be used."
                        )
                    poetry_lockfile = p.as_posix()
                context_files["/.poetry.lock"] = poetry_lockfile
                commands += ["COPY /.poetry.lock /tmp/poetry/poetry.lock"]

            # Indentation for back-compat TODO: fix when we update image_builder_version
            install_cmd = "  poetry install --no-root"

            if with_:
                install_cmd += f" --with {','.join(with_)}"

            if without:
                install_cmd += f" --without {','.join(without)}"

            if only:
                install_cmd += f" --only {','.join(only)}"
            install_cmd += " --compile"  # no .pyc compilation slows down cold-start.

            commands += [
                "COPY /.pyproject.toml /tmp/poetry/pyproject.toml",
                "RUN cd /tmp/poetry && \\ ",
                "  poetry config virtualenvs.create false && \\ ",
                install_cmd,
            ]
            return DockerfileSpec(commands=commands, context_files=context_files)

        return _Image._from_args(
            base_images={"base": self},
            dockerfile_function=build_dockerfile,
        )

    def dockerfile_commands(
        self,
        *dockerfile_commands: Union[str, List[str]],
        context_files: Dict[str, str] = {},
    ) -> "_Image":
        """Extend an image with arbitrary Dockerfile-like commands."""
        cmds = _flatten_str_args(
            "dockerfile_commands", "dockerfile_commands", dockerfile_commands
        )
        if not cmds:
            return self

        def build_dockerfile(version: ImageBuilderVersion) -> DockerfileSpec:
            return DockerfileSpec(
                commands=["FROM base", *cmds], context_files=context_files
            )

        return _Image._from_args(
            base_images={"base": self},
            dockerfile_function=build_dockerfile,
        )

    def run_commands(
        self,
        *commands: Union[str, List[str]],
    ) -> "_Image":
        """Extend an image with a list of shell commands to run."""
        cmds = _flatten_str_args("run_commands", "commands", commands)
        if not cmds:
            return self

        def build_dockerfile(version: ImageBuilderVersion) -> DockerfileSpec:
            return DockerfileSpec(
                commands=["FROM base"] + [f"RUN {cmd}" for cmd in cmds],
                context_files={},
            )

        return _Image._from_args(
            base_images={"base": self},
            dockerfile_function=build_dockerfile,
        )

    @staticmethod
    def conda(python_version: str = "3.9") -> "_Image":
        """
        A Conda base image, using miniconda3 and derived from the official Docker Hub image.
        In most cases, using [`Image.micromamba()`](/docs/reference/modal.Image#micromamba) with [`micromamba_install`](/docs/reference/modal.Image#micromamba_install) is recommended over `Image.conda()`, as it leads to significantly faster image build times.
        """
        _validate_python_version(python_version)

        def build_dockerfile(version: ImageBuilderVersion) -> DockerfileSpec:
            requirements_path = _get_client_requirements_path(python_version)
            context_files = {"/modal_requirements.txt": requirements_path}

            # Doesn't use the official continuumio/miniconda3 image as a base. That image has maintenance
            # issues (https://github.com/ContinuumIO/docker-images/issues) and building our own is more flexible.
            conda_install_script = (
                "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
            )
            commands = [
                "FROM debian:bullseye",  # the -slim images lack files required by Conda.
                # Temporarily add utility packages for conda installation.
                "RUN apt-get --quiet update && apt-get --quiet --yes install curl bzip2 \\",
                f"&& curl --silent --show-error --location {conda_install_script} --output /tmp/miniconda.sh \\",
                # Install miniconda to a filesystem location on the $PATH of Modal container tasks.
                # -b = install in batch mode w/o manual intervention.
                # -f = allow install prefix to already exist.
                # -p = the install prefix location.
                "&& bash /tmp/miniconda.sh -bfp /usr/local \\ ",
                "&& rm -rf /tmp/miniconda.sh",
                # Biggest and most stable community-led Conda channel.
                "RUN conda config --add channels conda-forge \\ ",
                # softlinking can put conda in a broken state, surfacing error on uninstall like:
                # `No such device or address: '/usr/local/lib/libz.so' -> '/usr/local/lib/libz.so.c~'`
                "&& conda config --set allow_softlinks false \\ ",
                # Install requested Python version from conda-forge channel; base debian image has only 3.7.
                f"&& conda install --yes --channel conda-forge python={python_version} \\ ",
                "&& conda update conda \\ ",
                # Remove now unneeded packages and files.
                "&& apt-get --quiet --yes remove curl bzip2 \\ ",
                "&& apt-get --quiet --yes autoremove \\ ",
                "&& apt-get autoclean \\ ",
                "&& rm -rf /var/lib/apt/lists/* /var/log/dpkg.log \\ ",
                "&& conda clean --all --yes",
                # Setup .bashrc for conda.
                "RUN conda init bash --verbose",
                "COPY /modal_requirements.txt /modal_requirements.txt",
                # .bashrc is explicitly sourced because RUN is a non-login shell and doesn't run bash.
                "RUN . /root/.bashrc && conda activate base \\ ",
                "&& python -m pip install --upgrade pip \\ ",
                "&& python -m pip install -r /modal_requirements.txt",
            ]
            return DockerfileSpec(commands=commands, context_files=context_files)

        base = _Image._from_args(
            dockerfile_function=build_dockerfile,
        )

        # TODO include these in the base image once we version the build?
        return base.dockerfile_commands(
            [
                "ENV CONDA_EXE=/usr/local/bin/conda",
                "ENV CONDA_PREFIX=/usr/local",
                "ENV CONDA_PROMPT_MODIFIER=(base)",
                "ENV CONDA_SHLVL=1",
                "ENV CONDA_PYTHON_EXE=/usr/local/bin/python",
                "ENV CONDA_DEFAULT_ENV=base",
            ]
        )

    def conda_install(
        self,
        *packages: Union[
            str, List[str]
        ],  # A list of Python packages, eg. ["numpy", "matplotlib>=3.5.0"]
        channels: List[
            str
        ] = [],  # A list of Conda channels, eg. ["conda-forge", "nvidia"]
    ) -> "_Image":
        """Install a list of additional packages using Conda. Note that in most cases, using [`Image.micromamba()`](/docs/reference/modal.Image#micromamba) with [`micromamba_install`](/docs/reference/modal.Image#micromamba_install)
        is recommended over `conda_install`, as it leads to significantly faster image build times.
        """

        pkgs = _flatten_str_args("conda_install", "packages", packages)
        if not pkgs:
            return self

        def build_dockerfile(version: ImageBuilderVersion) -> DockerfileSpec:
            package_args = " ".join(shlex.quote(pkg) for pkg in pkgs)
            channel_args = "".join(f" -c {channel}" for channel in channels)

            commands = [
                "FROM base",
                f"RUN conda install {package_args}{channel_args} --yes \\ ",
                "&& conda clean --yes --index-cache --tarballs --tempfiles --logfiles",
            ]
            return DockerfileSpec(commands=commands, context_files={})

        return _Image._from_args(
            base_images={"base": self},
            dockerfile_function=build_dockerfile,
        )

    def conda_update_from_environment(
        self,
        environment_yml: str,
    ) -> "_Image":
        """Update a Conda environment using dependencies from a given environment.yml file."""

        def build_dockerfile(version: ImageBuilderVersion) -> DockerfileSpec:
            context_files = {"/environment.yml": os.path.expanduser(environment_yml)}

            commands = [
                "FROM base",
                "COPY /environment.yml /environment.yml",
                "RUN conda env update --name base -f /environment.yml \\ ",
                "&& conda clean --yes --index-cache --tarballs --tempfiles --logfiles",
            ]
            return DockerfileSpec(commands=commands, context_files=context_files)

        return _Image._from_args(
            base_images={"base": self},
            dockerfile_function=build_dockerfile,
        )

    @staticmethod
    def micromamba(
        python_version: str = "3.9",
    ) -> "_Image":
        """
        A Micromamba base image. Micromamba allows for fast building of small Conda-based containers.
        In most cases it will be faster than using [`Image.conda()`](/docs/reference/modal.Image#conda).
        """
        _validate_python_version(python_version)

        def build_dockerfile(version: ImageBuilderVersion) -> DockerfileSpec:
            tag = "mambaorg/micromamba:1.3.1-bullseye-slim"
            setup_commands = [
                'SHELL ["/usr/local/bin/_dockerfile_shell.sh"]',
                "ENV MAMBA_DOCKERFILE_ACTIVATE=1",
                f"RUN micromamba install -n base -y python={python_version} pip -c conda-forge",
            ]
            commands = _Image._registry_setup_commands(
                tag, setup_commands, add_python=None
            )
            context_files = {
                "/modal_requirements.txt": _get_client_requirements_path(python_version)
            }
            return DockerfileSpec(commands=commands, context_files=context_files)

        return _Image._from_args(
            dockerfile_function=build_dockerfile,
        )

    def micromamba_install(
        self,
        # A list of Python packages, eg. ["numpy", "matplotlib>=3.5.0"]
        *packages: Union[str, List[str]],
        # A list of Conda channels, eg. ["conda-forge", "nvidia"]
        channels: List[str] = [],
    ) -> "_Image":
        """Install a list of additional packages using micromamba."""

        pkgs = _flatten_str_args("micromamba_install", "packages", packages)
        if not pkgs:
            return self

        def build_dockerfile(version: ImageBuilderVersion) -> DockerfileSpec:
            package_args = " ".join(shlex.quote(pkg) for pkg in pkgs)
            channel_args = "".join(f" -c {channel}" for channel in channels)

            commands = [
                "FROM base",
                f"RUN micromamba install {package_args}{channel_args} --yes",
            ]
            return DockerfileSpec(commands=commands, context_files={})

        return _Image._from_args(
            base_images={"base": self},
            dockerfile_function=build_dockerfile,
        )

    @staticmethod
    def _registry_setup_commands(
        tag: str, setup_commands: List[str], add_python: Optional[str]
    ) -> List[str]:
        add_python_commands: List[str] = []
        if add_python:
            python_version = add_python
            add_python_commands = [
                f"RUN apt-get update && apt-get install -y python{python_version} python{python_version}-dev wget",
                f"RUN ln -s /usr/bin/python{python_version} /usr/local/bin/python",
                "ENV TERMINFO_DIRS=/etc/terminfo:/lib/terminfo:/usr/share/terminfo:/usr/lib/terminfo",
                "RUN wget https://bootstrap.pypa.io/get-pip.py",
                "RUN python get-pip.py",
            ]
        return [
            f"FROM {tag}",
            *add_python_commands,
            *setup_commands,
            # "COPY /modal_requirements.txt /modal_requirements.txt",
            "RUN python -m pip install --upgrade pip",
            # "RUN python -m pip install -r /modal_requirements.txt",
            # TODO: We should add this next line at some point to clean up the image, but it would
            # trigger a hash change, so batch it with the next rebuild-triggering change.
            #
            # "RUN rm /modal_requirements.txt",
        ]

    @staticmethod
    def from_registry(
        tag: str,
        setup_dockerfile_commands: List[str] = [],
        add_python: Optional[str] = None,
        **kwargs,
    ) -> "_Image":
        """Build a Modal image from a public or private image registry, such as Docker Hub.

        The image must be built for the `linux/amd64` platform.

        If your image does not come with Python installed, you can use the `add_python` parameter
        to specify a version of Python to add to the image. Supported versions are `3.8`, `3.9`,
        `3.10`, `3.11`, and `3.12`. Otherwise, the image is expected to have Python>3.8 available
        on PATH as `python`, along with `pip`.

        You may also use `setup_dockerfile_commands` to run Dockerfile commands before the
        remaining commands run. This might be useful if you want a custom Python installation or to
        set a `SHELL`. Prefer `run_commands()` when possible though.

        To authenticate against a private registry with static credentials, you must set the `secret` parameter to
        a `modal.Secret` containing a username (`REGISTRY_USERNAME`) and an access token or password (`REGISTRY_PASSWORD`).

        To authenticate against private registries with credentials from a cloud provider, use `Image.from_gcp_artifact_registry()`
        or `Image.from_aws_ecr()`.

        **Examples**

        ```python
        modal.Image.from_registry("python:3.11-slim-bookworm")
        modal.Image.from_registry("ubuntu:22.04", add_python="3.11")
        modal.Image.from_registry("nvcr.io/nvidia/pytorch:22.12-py3")
        ```
        """

        def build_dockerfile(version: ImageBuilderVersion) -> DockerfileSpec:
            commands = _Image._registry_setup_commands(
                tag, setup_dockerfile_commands, add_python
            )
            context_files = {
                "/modal_requirements.txt": _get_client_requirements_path(add_python)
            }
            return DockerfileSpec(commands=commands, context_files=context_files)

        return _Image._from_args(
            dockerfile_function=build_dockerfile,
            **kwargs,
        )

    @staticmethod
    def from_dockerfile(
        path: Union[str, Path],
        *,
        add_python: Optional[str] = None,
    ) -> "_Image":
        """Build a Modal image from a local Dockerfile.

        If your Dockerfile does not have Python installed, you can use the `add_python` parameter
        to specify a version of Python to add to the image. Supported versions are `3.8`, `3.9`,
        `3.10`, `3.11`, and `3.12`.

        **Example**

        ```python
        image = modal.Image.from_dockerfile("./Dockerfile", add_python="3.12")
        ```
        """

        # --- Build the base dockerfile

        def build_dockerfile_base(version: ImageBuilderVersion) -> DockerfileSpec:
            with open(os.path.expanduser(path)) as f:
                commands = f.read().split("\n")
            return DockerfileSpec(commands=commands, context_files={})

        base_image = _Image._from_args(
            dockerfile_function=build_dockerfile_base,
        )

        # --- Now add in the modal dependencies, and, optionally a Python distribution
        # This happening in two steps is probably a vestigial consequence of previous limitations,
        # but it will be difficult to merge them without forcing rebuilds of images.

        def build_dockerfile_python(version: ImageBuilderVersion) -> DockerfileSpec:
            requirements_path = _get_client_requirements_path(add_python)

            add_python_commands = []
            if add_python:
                add_python_commands = [
                    "COPY /python/. /usr/local",
                    "RUN ln -s /usr/local/bin/python3 /usr/local/bin/python",
                    "ENV TERMINFO_DIRS=/etc/terminfo:/lib/terminfo:/usr/share/terminfo:/usr/lib/terminfo",
                ]

            commands = [
                "FROM base",
                *add_python_commands,
                "COPY /modal_requirements.txt /modal_requirements.txt",
                "RUN python -m pip install --upgrade pip",
                "RUN python -m pip install -r /modal_requirements.txt",
            ]

            context_files = {"/modal_requirements.txt": requirements_path}

            return DockerfileSpec(commands=commands, context_files=context_files)

        return _Image._from_args(
            base_images={"base": base_image},
            dockerfile_function=build_dockerfile_python,
        )

    @staticmethod
    def debian_slim(python_version: Optional[str] = None) -> "_Image":
        """Default image, based on the official `python:X.Y.Z-slim-bullseye` Docker images."""

        def build_dockerfile(version: ImageBuilderVersion) -> DockerfileSpec:
            full_python_version = _dockerhub_python_version(python_version)

            requirements_path = _get_client_requirements_path(full_python_version)
            commands = [
                f"FROM python:{full_python_version}-slim-bullseye",
                "COPY /modal_requirements.txt /modal_requirements.txt",
                "RUN apt-get update",
                "RUN apt-get install -y gcc gfortran build-essential",
                "RUN pip install --upgrade pip",
                "RUN pip install -r /modal_requirements.txt",
                # Set debian front-end to non-interactive to avoid users getting stuck with input
                # prompts.
                # "RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections",
            ]
            return DockerfileSpec(
                commands=commands,
                context_files={"/modal_requirements.txt": requirements_path},
            )

        return _Image._from_args(
            dockerfile_function=build_dockerfile,
        )

    def apt_install(
        self,
        *packages: Union[
            str, List[str]
        ],  # A list of packages, e.g. ["ssh", "libpq-dev"]
    ) -> "_Image":
        """Install a list of Debian packages using `apt`.

        **Example**

        ```python
        image = modal.Image.debian_slim().apt_install("git")
        ```
        """
        pkgs = _flatten_str_args("apt_install", "packages", packages)
        if not pkgs:
            return self

        package_args = " ".join(shlex.quote(pkg) for pkg in pkgs)

        def build_dockerfile(version: ImageBuilderVersion) -> DockerfileSpec:
            commands = [
                "FROM base",
                "RUN apt-get update",
                f"RUN apt-get install -y {package_args}",
            ]
            return DockerfileSpec(commands=commands, context_files={})

        return _Image._from_args(
            base_images={"base": self},
            dockerfile_function=build_dockerfile,
        )

    def env(self, vars: Dict[str, str]) -> "_Image":
        """Sets the environmental variables of the image.

        **Example**

        ```python
        image = (
            modal.Image.conda()
                .env({"CONDA_OVERRIDE_CUDA": "11.2"})
                .conda_install("jax", "cuda-nvcc", channels=["conda-forge", "nvidia"])
                .pip_install("dm-haiku", "optax")
        )
        ```
        """

        def build_dockerfile(version: ImageBuilderVersion) -> DockerfileSpec:
            commands = ["FROM base"] + [
                f"ENV {key}={shlex.quote(val)}" for (key, val) in vars.items()
            ]
            return DockerfileSpec(commands=commands, context_files={})

        return _Image._from_args(
            base_images={"base": self},
            dockerfile_function=build_dockerfile,
        )

    def workdir(self, path: str) -> "_Image":
        """Set the working directory for subsequent image build steps and function execution.

        **Example**

        ```python
        image = (
            modal.Image.debian_slim()
            .run_commands("git clone https://xyz app")
            .workdir("/app")
            .run_commands("yarn install")
        )
        ```
        """

        def build_dockerfile(version: ImageBuilderVersion) -> DockerfileSpec:
            commands = ["FROM base"] + [f"WORKDIR {shlex.quote(path)}"]
            return DockerfileSpec(commands=commands, context_files={})

        return _Image._from_args(
            base_images={"base": self},
            dockerfile_function=build_dockerfile,
        )

    def to_dockerfile(self) -> str:
        """Convert the image to a Dockerfile."""
        docker_file = ""

        for spec in self.commands:
            for command in spec.commands:
                if "FROM base" in command:
                    continue
                if "/modal_requirements.txt" in command:
                    continue
                docker_file += command + "\n"
            docker_file += "\n"

        return docker_file

    @contextlib.contextmanager
    def imports(self):
        try:
            yield
        except Exception as exc:
            self.inside_exceptions.append(exc)
            if not isinstance(exc, ImportError):
                warnings.warn(
                    f"Warning: caught a non-ImportError exception in an `imports()` block: {repr(exc)}"
                )


Image = _Image
