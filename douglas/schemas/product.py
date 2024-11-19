from pydantic import AnyHttpUrl, Field

from .base import BaseModel


class ProductVariant(BaseModel):
    name: str
    base_price: float | None = Field(None)
    original_price: float | None = Field(None)
    discounted_price: float | None = Field(None)


class ProductClassification(BaseModel):
    key: str
    value: str


class Product(BaseModel):
    url: AnyHttpUrl
    name: str
    code: str
    ean: str | None = Field(None)
    description: str | None = Field(None)
    image: AnyHttpUrl
    variant: list[ProductVariant]
    features: list[str]
    classifications: list[ProductClassification]
    average_rating: float | None = Field(None)
    number_of_reviews: int | None = Field(None)


class Paginated[T](BaseModel):
    page: int
    page_size: int
    total_pages: int
    items: list[T]
