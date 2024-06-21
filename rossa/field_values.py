from typing import Dict, List, Optional, Union

from pydantic import BaseModel

SelectFieldValue = Union[
    "OptionValue",
    List["OptionValue"],
]

FieldValue = Union[
    str,
    int,
    float,
    bool,
    List[str],
    List[int],
    List[float],
    List[bool],
    SelectFieldValue,
]


class OptionValue(BaseModel):
    type: Union[str, List[str]]
    settings: Dict[str, FieldValue] = {}

    def get_setting(self, key: str, default: Optional[FieldValue] = None) -> FieldValue:
        return self.settings.get(key, default)
