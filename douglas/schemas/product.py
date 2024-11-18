from pydantic import AnyHttpUrl, ConfigDict, Field

from .base import BaseModel


class ProductVariant(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    price: float


class ProductClassification(BaseModel):
    key: str
    value: str


class Product(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    url: AnyHttpUrl
    name: str
    ean: str | None = Field(None)
    description: str
    image: AnyHttpUrl
    variant: list[ProductVariant]
    features: list[str]
    classifications: list[ProductClassification]
    average_rating: float
    number_of_reviews: int
