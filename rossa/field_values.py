from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, create_model, validator


FieldValue = Union[
    int,
    float,
    str,
    bool,
    List[str],
    List[int],
    List[float],
    List[bool],
]


class OptionValue(BaseModel):
    type: Union[str, List[str]]
    settings: Dict[str, Any] = {}

    @validator("settings", pre=True)
    def validate_settings(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        SettingsModel = create_model(
            "SettingsModel",
            __root__=(
                Dict[str, Union[FieldValue, OptionValue, List[OptionValue]]],
                ...,
            ),
        )

        SettingsModel(__root__=v)
        return v

    def get_setting(self, key: str, default: Optional[Any] = None) -> Any:
        return self.settings.get(key, default)


SelectFieldValue = Union[
    OptionValue,
    List[OptionValue],
]

FieldValue = Union[
    FieldValue,
    SelectFieldValue,
]
