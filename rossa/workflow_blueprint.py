from typing import Any, Dict, Generator, List, Optional, Union

from .constants import SAFE_DEFAULT_FIELD_KEY, REAL_DEFAULT_FIELD_KEY
from .responses import Notification, Response
from .image import Image
from .fields import FieldType, Option
from abc import ABC, abstractmethod
from pydantic import Extra, validate_arguments, BaseModel
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

    def schema(self) -> Dict[str, Any]:
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

        def field_info_to_dict(
            field: FieldInfo, name: Optional[str] = None
        ) -> Dict[str, Any]:
            if not isinstance(field, FieldInfo):
                raise ValueError("Field must be a FieldInfo")

            OPTIONS_KEY = "options"
            TYPE_KEY = "type"

            extra = (
                field.extra
                if hasattr(field, "extra")
                else (
                    field.json_schema_extra
                    if hasattr(field, "json_schema_extra")
                    else {}
                )
            )

            if TYPE_KEY not in extra or extra[TYPE_KEY] not in set(FieldType):
                raise ValueError("Field type must be in FieldType.")

            name = name or field.alias

            if not name or not isinstance(name, str):
                raise ValueError("Field name must be a string")

            options = []

            def process_value(value: Any) -> Any:
                if isinstance(value, FieldInfo):
                    return field_info_to_dict(value)
                elif isinstance(value, list):
                    return [process_value(item) for item in value]
                elif isinstance(value, dict):
                    return {k: process_value(v) for k, v in value.items()}
                elif isinstance(value, BaseModel):
                    return value.dict()
                return value

            if OPTIONS_KEY in extra and isinstance(extra[OPTIONS_KEY], list):
                for option in extra[OPTIONS_KEY]:
                    if not isinstance(option, Option):
                        continue

                    option_dict = option.dict()
                    option_dict = {
                        key: process_value(value) for key, value in option_dict.items()
                    }
                    options.append(option_dict)

            if OPTIONS_KEY in extra:
                del extra[OPTIONS_KEY]

            if SAFE_DEFAULT_FIELD_KEY in extra:
                extra[REAL_DEFAULT_FIELD_KEY] = extra[SAFE_DEFAULT_FIELD_KEY]
                del extra[SAFE_DEFAULT_FIELD_KEY]

            # detele all values with None in the extra dict
            extra = {
                k: v.dict() if isinstance(v, BaseModel) else v
                for k, v in extra.items()
                if v is not None
            }

            return {
                "name": name,
                "title": field.title,
                "description": field.description,
                OPTIONS_KEY: options,
                **extra,
            }

        for name, param in parameters.items():
            default = param.default

            if default == inspect.Parameter.empty or not isinstance(default, FieldInfo):
                continue

            field = field_info_to_dict(default, name)

            if field is None:
                continue

            fields.append(field)

        new_schema = {
            "title": self.title,
            "version": self.version,
            "description": self.description,
            "examples": self.examples if isinstance(self.examples, list) else [],
            "fields": fields,
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
