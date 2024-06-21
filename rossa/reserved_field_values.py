from typing import Dict, List, Optional, Union

from .constants import INFLUENCE_FIELD_ALIAS, INFLUENCE_FIELD_DEFAULT

from .field_values import FieldValue, OptionValue


ReservedFieldValue = List["ControlValue"]


class ControlValue(OptionValue):
    type: str
    input_contents: List[str] = []
    output_contents: List[str] = []
    settings: Dict[str, Union[FieldValue, ReservedFieldValue]] = {}

    @property
    def influence(self) -> float:
        return self.get_setting(INFLUENCE_FIELD_ALIAS, INFLUENCE_FIELD_DEFAULT)

    def get_setting(
        self, key: str, default: Optional[Union[FieldValue, ReservedFieldValue]] = None
    ) -> Union[FieldValue, ReservedFieldValue]:
        return self.settings.get(key, default)
