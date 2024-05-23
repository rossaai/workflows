from typing import Any, Dict, Generator, List, Optional, Union
from .responses import Notification, Response
from .image import Image
from .fields import FieldType, Option
from abc import ABC, abstractmethod
from pydantic import Extra, validate_arguments
from pydantic.fields import FieldInfo
import inspect
from typing import Optional


ReturnResults = Union[
    Union[Response, Notification],
    List[Union[Response, Notification]],
]


class WorkflowBlueprint(ABC):
    image: Optional[Image] = None
    title: str
    version: str
    description: str
    examples: List[Dict[str, Any]] = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Get the original signature of the cls.run method
        cls.original_run = cls.run
        original_signature = inspect.signature(cls.original_run)

        # Apply the validate_arguments decorator to the original run method
        validated_run = validate_arguments(
            cls.original_run, config=dict(extra=Extra.ignore)
        )

        # Ignore extra arguments
        def run_wrapper(self, *args, **kwargs):
            # Extract only the arguments present in the original signature
            valid_kwargs = {
                k: v for k, v in kwargs.items() if k in original_signature.parameters
            }

            return validated_run(self, *args, **valid_kwargs)

        cls.run = run_wrapper

    def schema(self):
        # validate title, version, description
        if not isinstance(self.title, str):
            raise ValueError("title must be a string")
        if not isinstance(self.version, str):
            raise ValueError("version must be a string")
        if not isinstance(self.description, str):
            raise ValueError("description must be a string")

        fields = []

        # check if original_run is in the class and if it is a function
        # else use the run method
        run_fn = (
            self.original_run
            if hasattr(self, "original_run") and callable(self.original_run)
            else self.run
        )

        parameters = inspect.signature(run_fn).parameters

        for name, param in parameters.items():
            default = param.default

            is_not_valid_field = default == inspect.Parameter.empty or not isinstance(
                default, FieldInfo
            )

            if is_not_valid_field:
                continue

            extra = (
                default.extra
                if hasattr(default, "extra")
                else (
                    default.json_schema_extra
                    if hasattr(default, "json_schema_extra")
                    else {}
                )
            )
            is_not_valid_field = "type" not in default.extra and default.extra[
                "type"
            ] not in set(FieldType)

            if is_not_valid_field:
                continue

            options = []

            # validate if .options is a list and is in default.extra class
            if "options" in default.extra and isinstance(
                default.extra["options"], list
            ):
                for option in default.extra["options"]:
                    if isinstance(option, Option):
                        options.append(option.dict(by_alias=True))

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
            "fields": fields,
            "examples": self.examples if isinstance(self.examples, list) else [],
        }

        return new_schema

    def download(self):
        pass

    def load(self):
        pass

    @abstractmethod
    def run(self) -> Union[
        Generator[
            ReturnResults,
            None,
            None,
        ],
        ReturnResults,
    ]:
        pass
