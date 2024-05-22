from pydantic import BaseModel


class ShowFieldIfValue(BaseModel):
    field: str
    value: str
