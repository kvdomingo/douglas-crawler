from httpx import AsyncClient

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
        page: int = 1,
        page_size: int = 50,
    ):
        """Search for products in a specific product category."""

        res = await self.client.get(
            f"/products/search/category/{category_id}",
            params=DouglasAPIProductListParams(
                page=page,
                pageSize=page_size,
            ).model_dump(),
        )
        res.raise_for_status()
        products = res.json().get("products", [])
        return [DouglasAPIProductListItem.model_validate(p) for p in products]

    async def get(self, id: str):
        res = await self.client.get(
            f"/products/{id}",
            params=DouglasAPIProductDetailParams().model_dump(),
        )
        res.raise_for_status()
        return DouglasProductDetail.model_validate(res.json())


class DouglasAPI:
    client = AsyncClient(
        base_url=str(settings.API_BASE_URL),
        headers={
            "Accept": "application/json",
            "Accept-Encoding": "gzip,deflate,br,zstd",
            "Cache-Control": "no-cache",
            "User-Agent": settings.USER_AGENT,
        },
    )

    def __init__(self):
        self.product = _Product(client=self.client)


class DouglasAPIArgs(BaseModel):
    product_code: str
