"""init

Revision ID: bd3c5d0ca4d4
Revises:
Create Date: 2024-11-18 12:08:22.533627

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bd3c5d0ca4d4"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text("""
        CREATE TABLE products (
            id VARCHAR(26) NOT NULL,
            code TEXT NOT NULL,
            ean TEXT NOT NULL,
            url TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            average_rating FLOAT,
            number_of_reviews INTEGER,
            image TEXT NOT NULL,
            features TEXT[] NOT NULL,

            CONSTRAINT pk_products PRIMARY KEY (id),
            CONSTRAINT uq_products_code UNIQUE (code),
            CONSTRAINT uq_products_ean UNIQUE (ean)
        );

        CREATE INDEX ix_products_id ON products (id);
        CREATE INDEX ix_products_code ON products (code);
        CREATE INDEX ix_products_ean ON products (ean);

        CREATE TABLE product_variants (
            id VARCHAR(26) NOT NULL,
            product_id VARCHAR(26) NOT NULL,
            name TEXT NOT NULL,
            base_price FLOAT NOT NULL,
            original_price FLOAT,
            discounted_price FLOAT,

            CONSTRAINT pk_product_variants PRIMARY KEY (id),
            CONSTRAINT fk_product_variants_product_id FOREIGN KEY (product_id) REFERENCES products (id),
            CONSTRAINT uq_product_variants_product_id_name UNIQUE (product_id, name)
        );

        CREATE INDEX ix_product_variants_id ON product_variants (id);

        CREATE TABLE product_classifications (
            id VARCHAR(26) NOT NULL,
            product_id VARCHAR(26) NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,

            CONSTRAINT pk_product_classifications PRIMARY KEY (id),
            CONSTRAINT fk_product_classifications_product_id FOREIGN KEY (product_id) REFERENCES products (id),
            CONSTRAINT uq_product_classifications_product_id_key UNIQUE (product_id, key)
        );

        CREATE INDEX ix_product_classifications_id ON product_classifications (id);
        """)
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text("""
        DROP INDEX ix_product_classifications_id;
        DROP TABLE product_classifications;

        DROP INDEX ix_product_variants_id;
        DROP TABLE product_variants;

        DROP INDEX ix_products_ean;
        DROP INDEX ix_products_code;
        DROP INDEX ix_products_id;
        DROP TABLE products;
        """)
    )
