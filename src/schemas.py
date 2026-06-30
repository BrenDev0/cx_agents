from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

class ApiSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        serialize_by_alias=True,
        populate_by_name=True,
        str_min_length=1,
        str_strip_whitespace=True,
        extra="forbid"
    )