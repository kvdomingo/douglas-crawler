from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class Product(BaseModel):
    __tablename__ = "products"

    url: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column()
    image: Mapped[str] = mapped_column()
    labels: Mapped[list[str]] = mapped_column()
    properties: Mapped[dict] = mapped_column()
    description: Mapped[str] = mapped_column()
    avg_rating: Mapped[float] = mapped_column()
    total_ratings: Mapped[int] = mapped_column()
    variant: Mapped[list["ProductVariant"]] = relationship(back_populates="product")


class ProductVariant(BaseModel):
    __tablename__ = "product_variants"

    product: Mapped["Product"] = relationship("Product", back_populates="variants")
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"))
    name: Mapped[str] = mapped_column()
    price: Mapped[float] = mapped_column()
