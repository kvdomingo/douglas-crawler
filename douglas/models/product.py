from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel, ulid_factory


class Product(BaseModel):
    __tablename__ = "products"

    ean: Mapped[str] = mapped_column(index=True, unique=True, primary_key=True)
    code: Mapped[str] = mapped_column(index=True)
    url: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column(nullable=True)
    average_rating: Mapped[float] = mapped_column(nullable=True)
    number_of_reviews: Mapped[int] = mapped_column(nullable=True)
    image: Mapped[str] = mapped_column()
    features: Mapped[list[str]] = mapped_column()
    classifications: Mapped[list["ProductClassification"]] = relationship(
        back_populates="product"
    )
    variants: Mapped[list["ProductVariant"]] = relationship(back_populates="product")


class ProductVariant(BaseModel):
    __tablename__ = "product_variants"
    __table_args__ = (
        UniqueConstraint(
            "product_id", "name", name="uq_product_variants_product_id_name"
        ),
    )

    id: Mapped[str] = mapped_column(
        primary_key=True, unique=True, index=True, default=ulid_factory
    )
    product: Mapped["Product"] = relationship("Product", back_populates="variants")
    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.ean", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column()
    base_price: Mapped[float] = mapped_column()
    original_price: Mapped[float] = mapped_column(nullable=True)
    discounted_price: Mapped[float] = mapped_column(nullable=True)


class ProductClassification(BaseModel):
    __tablename__ = "product_classifications"
    __table_args__ = (
        UniqueConstraint(
            "product_id", "key", name="uq_product_classifications_product_id_key"
        ),
    )

    id: Mapped[str] = mapped_column(
        primary_key=True, unique=True, index=True, default=ulid_factory
    )
    product: Mapped["Product"] = relationship(
        "Product", back_populates="classifications"
    )
    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.ean", ondelete="CASCADE")
    )
    key: Mapped[str] = mapped_column()
    value: Mapped[str] = mapped_column()
