from typing import Any

from pydantic import AnyHttpUrl, ConfigDict

from .base import BaseModel


class ProductVariant(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    price: float


class Product(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    url: AnyHttpUrl
    name: str
    description: str
    image: AnyHttpUrl
    variant: list[ProductVariant]
    features: list[str]
    classifications: dict[str, Any]
    avg_rating: float
    total_ratings: int
    ean: str
