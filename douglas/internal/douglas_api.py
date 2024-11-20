from httpx import AsyncClient
from pydantic import Field

from douglas.schemas import (
    BaseModel,
    DouglasAPIProductDetailParams,
    DouglasAPIProductListItem,
    DouglasAPIProductListParams,
    DouglasProductDetail,
)
from douglas.settings import settings


class _Product:
    def __init__(self, client: AsyncClient):
        self.client = client

    async def search_in_category(
        self,
        category_id: str,
        page: int = 0,
    ):
        """
        Search for products in a specific product category.

        Args:
            category_id: Douglas category ID, e.g. if the category page URL is
                https://www.douglas.de/de/c/gesicht/gesichtsmasken/feuchtigkeitsmasken/120308, the category ID is
                120308.
            page: Page number.

        Returns:
            A list of products for the given page number.
        """

        res = await self.client.get(
            f"/jsapi/v2/products/search/category/{category_id}",
            params=DouglasAPIProductListParams(currentPage=page).model_dump(),
        )
        res.raise_for_status()
        products = res.json().get("products", [])
        return [DouglasAPIProductListItem.model_validate(p) for p in products]

    async def get(self, id: str):
        """
        Get product details by ID/code.

        Args:
            id: Product ID/code, e.g. if the product page URL is https://www.douglas.de/de/p/3001055831?variant=077163,
            the product code is 3001055831.

        Returns:
            The product details.
        """
        res = await self.client.get(
            f"/api/v2/products/{id}",
            params=DouglasAPIProductDetailParams().model_dump(),
        )
        res.raise_for_status()
        return DouglasProductDetail.model_validate(res.json())


class DouglasAPI:
    default_client_params = {
        "base_url": str(settings.BASE_URL),
        "headers": {
            "Accept": "application/json",
            "Accept-Encoding": "gzip,deflate,br,zstd",
            "Cache-Control": "no-cache",
            "User-Agent": settings.USER_AGENT,
        },
    }

    def __init__(self, client: AsyncClient = None):
        """
        Args:
            client: Client override if you want to manage the HTTPX client externally.
            If not provided, each class instance will use its own client.
        """
        self.client = client or self.default_client_factory()
        self.product = _Product(client=self.client)

    def default_client_factory(self):
        """
        Returns:
              client: Default HTTPX client
        """
        return AsyncClient(**self.default_client_params)


class DouglasAPIArgs(BaseModel):
    category_code: str
    page: int = Field(0, ge=0)
