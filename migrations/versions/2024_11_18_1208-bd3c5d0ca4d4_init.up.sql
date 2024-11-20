CREATE TABLE products
(
    ean               TEXT   NOT NULL,
    code              TEXT   NOT NULL,
    url               TEXT   NOT NULL,
    name              TEXT   NOT NULL,
    description       TEXT,
    average_rating    FLOAT,
    number_of_reviews INTEGER,
    image             TEXT   NOT NULL,
    features          TEXT[] NOT NULL,

    CONSTRAINT pk_products PRIMARY KEY (ean)
);

CREATE INDEX ix_products_ean ON products (ean);
CREATE INDEX ix_products_code ON products (code);

CREATE TABLE product_variants
(
    id               VARCHAR(26) NOT NULL,
    product_id       TEXT        NOT NULL,
    name             TEXT        NOT NULL,
    base_price       FLOAT       NOT NULL,
    original_price   FLOAT,
    discounted_price FLOAT,

    CONSTRAINT pk_product_variants PRIMARY KEY (id),
    CONSTRAINT fk_product_variants_product_id FOREIGN KEY (product_id) REFERENCES products (ean) ON DELETE CASCADE,
    CONSTRAINT uq_product_variants_product_id_name UNIQUE (product_id, name)
);

CREATE INDEX ix_product_variants_id ON product_variants (id);

CREATE TABLE product_classifications
(
    id         VARCHAR(26) NOT NULL,
    product_id TEXT        NOT NULL,
    key        TEXT        NOT NULL,
    value      TEXT        NOT NULL,

    CONSTRAINT pk_product_classifications PRIMARY KEY (id),
    CONSTRAINT fk_product_classifications_product_id FOREIGN KEY (product_id) REFERENCES products (ean) ON DELETE CASCADE,
    CONSTRAINT uq_product_classifications_product_id_key UNIQUE (product_id, key)
);

CREATE INDEX ix_product_classifications_id ON product_classifications (id);
