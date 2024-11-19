from pydantic import AnyHttpUrl, BaseModel, Field


class DouglasAPIProductListParams(BaseModel):
    fields: str = Field("FULL")
    isApp: bool = Field(False)
    isAppleDevice: bool = Field(False)
    isCriteoConsent: bool = Field(False)
    isCriteoEnabled: bool = Field(False)
    isMobile: bool = Field(False)
    isOwnBrandEnabled: bool = Field(False)
    isSSR: bool = Field(False)
    currentPage: int = Field(0, ge=0)


class DouglasAPIProductDetailParams(BaseModel):
    fields: str = Field("FULL")


class DouglasAPIProductListItemImage(BaseModel):
    url: AnyHttpUrl


class DouglasAPIProductPrice(BaseModel):
    currencyIso: str
    value: float
    originalValue: float | None = Field(None)
    discountPercentage: float | None = Field(None)


class DouglasAPIProductListItem(BaseModel):
    code: str
    url: str
    description: str | None = Field(None)
    averageRating: float
    numberOfReviews: int | None = Field(None)
    price: DouglasAPIProductPrice
    images: list[DouglasAPIProductListItemImage]
    baseProduct: str
    baseProductName: str | None = Field(None)


class DouglasAPIProductDetailBrandImage(DouglasAPIProductListItemImage):
    width: int | None = Field(None)
    height: int | None = Field(None)


class DouglasAPIProductDetailImage(DouglasAPIProductDetailBrandImage):
    format: str


class DouglasProductDetailClassificationFeatureValue(BaseModel):
    code: str | None = Field(None)
    value: str


class DouglasProductDetailClassificationFeature(BaseModel):
    code: str
    name: str
    featureValues: list[DouglasProductDetailClassificationFeatureValue]


class DouglasProductDetailClassification(BaseModel):
    code: str
    name: str
    features: list[DouglasProductDetailClassificationFeature] | None = Field(None)


class DouglasProductDetailVariantOption(BaseModel):
    code: str
    url: str
    priceData: DouglasAPIProductPrice
    variantName: str
    previewImage: DouglasAPIProductDetailImage
    images: list[DouglasAPIProductDetailImage]


class DouglasProductDetail(BaseModel):
    code: str
    url: str
    ean: str
    baseProduct: str
    baseProductUrl: str
    baseProductName: str | None = Field(None)
    description: str | None = Field(None)
    averageRating: float
    numberOfReviews: int
    images: list[DouglasAPIProductDetailImage]
    classifications: list[DouglasProductDetailClassification] = Field(
        default_factory=list
    )
    variantOptions: list[DouglasProductDetailVariantOption]
