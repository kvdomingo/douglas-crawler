from sqlalchemy import VARCHAR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from ulid import ULID


class BaseModel(DeclarativeBase):
    id: Mapped[str] = mapped_column(
        VARCHAR(26),
        primary_key=True,
        index=True,
        unique=True,
        default=ULID,
    )
