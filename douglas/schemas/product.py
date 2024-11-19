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
    code: str
    ean: str | None = Field(None)
    url: AnyHttpUrl
    name: str
    description: str | None = Field(None)
    average_rating: float | None = Field(None)
    number_of_reviews: int | None = Field(None)
    image: AnyHttpUrl
    features: list[str]
    classifications: list[ProductClassification]
    variants: list[ProductVariant]


class Paginated[T](BaseModel):
    page: int
    page_size: int
    total_pages: int
    items: list[T]
