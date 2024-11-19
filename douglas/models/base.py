from sqlalchemy import ARRAY, JSON, TEXT, VARCHAR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from ulid import ULID


def ulid_factory() -> str:
    return str(ULID())


class BaseModel(DeclarativeBase):
    type_annotation_map = {
        dict: JSON,
        list[str]: ARRAY(TEXT),
    }

    id: Mapped[str] = mapped_column(
        VARCHAR(26),
        primary_key=True,
        index=True,
        unique=True,
        default=ulid_factory,
    )
