from pydantic import (
    BaseModel as PydanticBaseModel,
    ConfigDict,
)


class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(from_attributes=True)
