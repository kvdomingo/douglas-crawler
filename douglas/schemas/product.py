from typing import Any

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field


class ProductVariant(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(description="Name of the variant")
    price: float = Field(description="Price of the variant")


class Product(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    url: AnyHttpUrl = Field(description="Link to the product")
    name: str = Field(description="Name of the product")
    image: AnyHttpUrl = Field(description="Link to image of the product")
    variant: list[ProductVariant] = Field(description="Variants of the product")
    product_labels: list[str] = Field(description="Labels of the product")
    product_details: dict[str, Any] = Field(description="Details of the product")
    description: str = Field(description="Description of the product")
    avg_rating: float = Field(description="Average rating of the product")
    total_ratings: int = Field(description="Total ratings of the product")
