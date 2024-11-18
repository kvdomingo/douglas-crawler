from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class Product(BaseModel):
    __tablename__ = "products"

    code: Mapped[str] = mapped_column(unique=True)
    ean: Mapped[str] = mapped_column(unique=True)
    url: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    average_rating: Mapped[float] = mapped_column()
    number_of_reviews: Mapped[int] = mapped_column()
    price: Mapped[float] = mapped_column()
    original_price: Mapped[float] = mapped_column()
    currency: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column()
    image: Mapped[str] = mapped_column()
    features: Mapped[list[str]] = mapped_column()
    classifications: Mapped[dict[str, str]] = mapped_column()
    variant: Mapped[list["ProductVariant"]] = relationship(back_populates="product")


class ProductVariant(BaseModel):
    __tablename__ = "product_variants"

    product: Mapped["Product"] = relationship("Product", back_populates="variants")
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"))
    name: Mapped[str] = mapped_column()
    price: Mapped[float] = mapped_column()
    originalPrice: Mapped[float] = mapped_column()
    currency: Mapped[str] = mapped_column()
