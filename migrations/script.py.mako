"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union
from pathlib import Path

from alembic import op
import sqlalchemy as sa

from douglas.settings import settings
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}

migrations_dir = settings.BASE_DIR / "migrations/versions"
file_stem = Path(__file__).stem


def upgrade() -> None:
    conn = op.get_bind()
    ${upgrades if upgrades else ""}


def downgrade() -> None:
    conn = op.get_bind()
    ${downgrades if downgrades else ""}
