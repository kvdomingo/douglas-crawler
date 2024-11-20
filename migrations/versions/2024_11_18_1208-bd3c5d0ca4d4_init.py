"""init

Revision ID: bd3c5d0ca4d4
Revises:
Create Date: 2024-11-18 12:08:22.533627

"""

from collections.abc import Sequence
from pathlib import Path

import sqlalchemy as sa
from alembic import op

from douglas.settings import settings

# revision identifiers, used by Alembic.
revision: str = "bd3c5d0ca4d4"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

migrations_dir = settings.BASE_DIR / "migrations/versions"
file_stem = Path(__file__).stem


def upgrade() -> None:
    with open(migrations_dir / f"{file_stem}.up.sql") as fh:
        sql = fh.read()

    conn = op.get_bind()
    conn.execute(sa.text(sql))


def downgrade() -> None:
    with open(migrations_dir / f"{file_stem}.down.sql") as fh:
        sql = fh.read()

    conn = op.get_bind()
    conn.execute(sa.text(sql))
