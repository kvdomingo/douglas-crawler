import re
from typing import Any

from bs4 import BeautifulSoup
from httpx import AsyncClient, AsyncHTTPTransport
from pydantic import AnyHttpUrl

from douglas.internal.douglas_api import DouglasAPI
from douglas.schemas import (
    BaseModel,
    Paginated,
    Product,
    ProductClassification,
    ProductVariant,
)
from douglas.settings import settings


class DouglasCrawlerArgs(BaseModel):
    url: AnyHttpUrl


class _Product:
    def __init__(self, client: AsyncClient):
        self.client = client

    async def search(self, url: AnyHttpUrl, page: int = 1) -> Paginated[str]:
        html = await self.fetch_raw_html(url)
        soup = await self.parse_html(html)
        num_pages = self.get_number_of_pages(soup)
        links = [
            s.find("a").get("href")
            for s in soup.find_all("div", {"class": "product-tile"})
        ]
        return Paginated(
            page=page,
            page_size=len(links),
            total_pages=num_pages,
            items=links,
        )

    async def get(self, url: AnyHttpUrl) -> Product:
        html = await self.fetch_raw_html(url)
        soup = await self.parse_html(html)

        ratings = self.get_ratings(soup)
        return Product(
            url=str(url),
            code=self.get_code(soup),
            ean=await self.get_ean(soup),
            name=self.get_name(soup),
            image=self.get_image(soup),
            variants=[
                ProductVariant.model_validate(v) for v in self.get_variants(soup)
            ],
            features=self.get_labels(soup),
            classifications=[
                ProductClassification.model_validate(p)
                for p in self.get_properties(soup)
            ],
            description=self.get_description(soup),
            average_rating=ratings["avg_rating"],
            number_of_reviews=ratings["total_ratings"],
        )

    async def fetch_raw_html(
        self,
        url: AnyHttpUrl,
        params: dict[str, str] = None,
        headers: dict[str, str] = None,
    ):
        res = await self.client.get(
            str(url),
            headers={
                **(headers or {}),
                "Accept": "text/html",
                "Accept-Encoding": "gzip,deflate,br,zstd",
                "Accept-Language": "en-US,en",
                "User-Agent": settings.USER_AGENT,
            },
            params=params or {},
        )
        return res.content.decode("utf-8")

    @staticmethod
    async def parse_html(html: str):
        return BeautifulSoup(html, "lxml")

    @staticmethod
    def get_name(soup: BeautifulSoup) -> str:
        s = soup.find("div", {"class": "brand-line__container"})
        brand_name = ""

        if (s_brand := s.find("a", {"class": "brand-line"})) is not None:
            brand_name = f"{s_brand.text} "

        product_name = s.find("span", {"class": "header-name"}).text
        return f"{brand_name}{product_name}"

    @staticmethod
    def get_image(soup: BeautifulSoup) -> str:
        return soup.find("img", {"class": "image swiper-lazy"}).get("data-lazy-src")

    @staticmethod
    def get_variants(soup: BeautifulSoup) -> list[dict[str, Any]]:
        out = []
        for s in soup.find_all("div", {"class": "product-detail__variant-row"}):
            obj = {
                "name": s.find("div", {"class": "product-detail__variant-name"}).text,
                "base_price": re.search(
                    r"\d+\.\d+",
                    s.find("span", {"class": "product-price__price"})
                    .text.replace("\xa0", " ")
                    .replace(",", "."),
                    flags=re.I,
                ).group(),
            }

            if (
                s_price_discount := s.find("div", {"class": "product-price__discount"})
            ) is not None:
                obj["discounted_price"] = re.search(
                    r"\d+\.\d+", s_price_discount.text.replace(",", "."), flags=re.I
                ).group()

            if (
                s_price_original := s.find("div", {"class": "product-price__original"})
            ) is not None:
                obj["original_price"] = re.search(
                    r"\d+\.\d+", s_price_original.text.replace(",", "."), flags=re.I
                ).group()

            out.append(obj)

        return out

    @staticmethod
    def get_labels(soup: BeautifulSoup) -> list[str]:
        if (s_label := soup.find("div", {"class": "product-labels"})) is not None:
            return [
                s.text
                for s in s_label.find_all("span", {"class": "product-label__name"})
            ]

        return []

    @staticmethod
    def get_properties(soup: BeautifulSoup) -> list[dict[str, str]]:
        properties = []
        for s in soup.find(
            "div", {"data-testid": "product-detail-info__classifications"}
        ).find_all("div"):
            props = s.find_all("span")
            if len(props) > 1:
                properties.append(
                    {
                        "key": props[0].text,
                        "value": props[1].text,
                    }
                )

        return properties

    def get_code(self, soup: BeautifulSoup) -> str:
        properties = self.get_properties(soup)
        return next(p["value"] for p in properties if p["key"].lower() == "art-nr.")

    @staticmethod
    def get_description(soup: BeautifulSoup) -> str | None:
        if (
            s := soup.find("div", {"class": "truncate product-details__description"})
        ) is not None:
            return s.text

        return None

    @staticmethod
    def get_ratings(soup: BeautifulSoup) -> dict[str, str | None]:
        rating_block = soup.find("span", {"class": "ratings-info"}).text.replace(
            "\xa0", " "
        )

        total_ratings = None
        if (
            re_total_ratings := re.search(r"\(\d+\)$", rating_block, flags=re.I)
        ) is not None:
            total_ratings = re_total_ratings.group().strip("()")

        avg_rating = None
        if (
            re_avg_rating := re.search(r"^\d+\.\d+", rating_block, flags=re.I)
        ) is not None:
            avg_rating = re_avg_rating.group()

        return {"avg_rating": avg_rating, "total_ratings": total_ratings}

    @staticmethod
    def get_number_of_pages(soup: BeautifulSoup) -> int:
        return int(
            re.search(
                r"\d+$",
                soup.find("div", {"class": "pagination-title"}).text,
                flags=re.I,
            ).group()
        )

    async def get_ean(self, soup: BeautifulSoup) -> str | None:
        api = DouglasAPI()
        product = await api.product.get(self.get_code(soup))
        return product.ean


class DouglasCrawler:
    transport = AsyncHTTPTransport(retries=3, http2=True)

    def __init__(self, client: AsyncClient = None):
        """
        Args:
            client: Client override if you want to manage the HTTPX client externally.
            If not provided, each class instance will use its own client.
        """

        self.client = client or self.default_client_factory()
        self.product = _Product(self.client)

    def default_client_factory(self):
        """
        Returns:
              client: Default HTTPX client
        """
        return AsyncClient(transport=self.transport)
