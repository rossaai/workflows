from typing import Any, Dict, List, Optional, Union

from pydantic import create_model, validator

from .constants import INTENSITY_FIELD_ALIAS, INTENSITY_FIELD_DEFAULT

from .field_values import FieldValue, OptionValue


class ControlValue(OptionValue):
    type: str
    input_contents: List[str] = []
    output_contents: List[str] = []
    settings: Dict[str, Any] = {}

    @validator("settings", pre=True)
    def validate_settings(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        SettingsModel = create_model(
            "SettingsModel",
            __root__=(
                Dict[str, Union[List[ControlValue], FieldValue]],
                ...,
            ),
        )

        SettingsModel(__root__=v)
        return v

    @property
    def influence(self) -> float:
        return float(self.get_setting(INTENSITY_FIELD_ALIAS, INTENSITY_FIELD_DEFAULT))

    def get_setting(
        self,
        key: str,
        default: Optional[Any] = None,
    ) -> Any:
        return self.settings.get(key, default)


ReservedFieldValue = List[ControlValue]
