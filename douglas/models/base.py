from sqlalchemy import JSON, VARCHAR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from ulid import ULID


class BaseModel(DeclarativeBase):
    type_annotation_map = {
        dict: JSON,
    }

    id: Mapped[str] = mapped_column(
        VARCHAR(26),
        primary_key=True,
        index=True,
        unique=True,
        default=ULID,
    )
