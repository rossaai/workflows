from typing import List, Union
from pydantic import BaseModel


class IfValue(BaseModel):
    type: str = "if_value"
    field: str
    value: str


class IfNotValue(BaseModel):
    type: str = "if_not_value"
    field: str
    value: str


class IfMinLength(BaseModel):
    type: str = "if_min_length"
    field: str
    min_length: int


class IfMaxLength(BaseModel):
    type: str = "if_max_length"
    field: str
    max_length: int


FieldConditional = Union[IfValue, IfNotValue, IfMinLength, IfMaxLength]

FieldConditionals = Union[List[FieldConditional], FieldConditional]
