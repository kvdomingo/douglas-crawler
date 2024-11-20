from sqlalchemy import ARRAY, JSON, TEXT
from sqlalchemy.orm import DeclarativeBase
from ulid import ULID


def ulid_factory() -> str:
    return str(ULID())


class BaseModel(DeclarativeBase):
    type_annotation_map = {
        dict: JSON,
        list[str]: ARRAY(TEXT),
    }
