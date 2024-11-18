from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class Product(BaseModel):
    __tablename__ = "products"

    code: Mapped[str] = mapped_column(unique=True, index=True)
    ean: Mapped[str] = mapped_column(unique=True, index=True)
    url: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column(nullable=True)
    average_rating: Mapped[float] = mapped_column()
    number_of_reviews: Mapped[int] = mapped_column()
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

    product: Mapped["Product"] = relationship("Product", back_populates="variants")
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"))
    name: Mapped[str] = mapped_column()
    base_price: Mapped[float] = mapped_column()
    original_price: Mapped[float] = mapped_column(nullable=True)
    discounted_price: Mapped[float] = mapped_column(nullable=True)
    currency: Mapped[str] = mapped_column()


class ProductClassification(BaseModel):
    __tablename__ = "product_classifications"
    __table_args__ = (
        UniqueConstraint(
            "product_id", "key", name="uq_product_classifications_product_id_key"
        ),
    )

    product: Mapped["Product"] = relationship(
        "Product", back_populates="classifications"
    )
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"))
    key: Mapped[str] = mapped_column()
    value: Mapped[str] = mapped_column()
