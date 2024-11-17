from pydantic import AnyHttpUrl, Field

from douglas.models import BaseModel


class DouglasAPIProductListParams(BaseModel):
    fields: str = Field("FULL")
    isApp: bool = Field(False)
    isAppleDevice: bool = Field(False)
    isCriteoConsent: bool = Field(False)
    isCriteoEnabled: bool = Field(False)
    isMobile: bool = Field(False)
    isOwnBrandEnabled: bool = Field(False)
    isSSR: bool = Field(False)
    pageSize: int = Field(50)
    page: int = Field(1)


class DouglasAPIProductDetailParams(BaseModel):
    fields: str = Field("FULL")


class DouglasAPIProductListItemImage(BaseModel):
    url: AnyHttpUrl


class DouglasAPIProductPrice(BaseModel):
    currencyIso: str
    value: float
    originalValue: float
    discountPercentage: float


class DouglasAPIProductListItem(BaseModel):
    code: str
    url: str
    description: str
    averageRating: float
    numberOfReviews: int
    price: DouglasAPIProductPrice
    images: list[DouglasAPIProductListItemImage]
    baseProduct: str
    baseProductName: str


class DouglasAPIProductDetailBrandImage(DouglasAPIProductListItemImage):
    width: int
    height: int


class DouglasAPIProductDetailImage(DouglasAPIProductDetailBrandImage):
    format: str


class DouglasProductDetailCategory(BaseModel):
    code: str
    name: str


class DouglasProductDetailClassificationFeatureValue(BaseModel):
    code: str
    value: str


class DouglasProductDetailClassificationFeature(BaseModel):
    code: str
    name: str
    featureValues: list[DouglasProductDetailClassificationFeatureValue]


class DouglasProductDetailClassification(BaseModel):
    code: str
    name: str
    features: list[DouglasProductDetailClassificationFeature]


class DouglasProductDetailVariantOption(BaseModel):
    code: str
    url: str
    priceData: DouglasAPIProductPrice
    variantName: str
    previewImage: DouglasAPIProductDetailImage
    images: list[DouglasAPIProductDetailImage]


class DouglasProductDetailBaseOption(BaseModel):
    variantType: str
    selected: DouglasProductDetailVariantOption


class DouglasProductDetailBrand(BaseModel):
    code: str
    name: str
    url: str
    image: DouglasAPIProductDetailBrandImage
    svgLogo: DouglasAPIProductDetailBrandImage
    alternateSvgLogo: DouglasAPIProductDetailBrandImage


class DouglasProductDetail(BaseModel):
    code: str
    url: str
    description: str
    averageRating: float
    numberOfReviews: int
    price: DouglasAPIProductPrice
    baseProduct: str
    images: list[DouglasAPIProductDetailImage]
    categories: list[DouglasProductDetailCategory]
    classifications: list[DouglasProductDetailClassification]
    variantOptions: list[DouglasProductDetailVariantOption]
    baseOptions: list[DouglasProductDetailBaseOption]
    baseContentPrice: DouglasAPIProductPrice
    application: str
    ingredients: str
    baseProductUrl: str
    baseProductName: str
    ean: str
    brand: DouglasProductDetailBrand
