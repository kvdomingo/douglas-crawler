import re
from typing import Any

from bs4 import BeautifulSoup
from httpx import AsyncClient, AsyncHTTPTransport
from loguru import logger
from pydantic import AnyHttpUrl

from douglas.internal.douglas_api import DouglasAPI
from douglas.schemas import BaseModel, Product, ProductClassification, ProductVariant
from douglas.settings import settings


class DouglasCrawlerArgs(BaseModel):
    url: AnyHttpUrl


class DouglasCrawler:
    transport = AsyncHTTPTransport(retries=3, http2=True)
    client = AsyncClient(transport=transport)
    soup: BeautifulSoup
    raw_html: str

    def __init__(self, args: DouglasCrawlerArgs):
        self.url = args.url

    async def __call__(self, *args, **kwargs):
        await self.fetch_raw_html()
        await self.parse_html(self.raw_html)

        ratings = self.get_ratings()
        return Product(
            url=str(self.url),
            code=self.get_code(),
            ean=await self.get_ean(),
            name=self.get_name(),
            image=self.get_image(),
            variant=[ProductVariant.model_validate(v) for v in self.get_variants()],
            features=self.get_labels(),
            classifications=[
                ProductClassification.model_validate(p) for p in self.get_properties()
            ],
            description=self.get_description(),
            average_rating=ratings["avg_rating"],
            number_of_reviews=ratings["total_ratings"],
        )

    async def fetch_raw_html(self):
        logger.info(f"Crawling {self.url}...")
        res = await self.client.get(
            str(self.url),
            headers={
                "Accept": "text/html",
                "Accept-Encoding": "gzip,deflate,br,zstd",
                "Accept-Language": "en-US,en",
                "User-Agent": settings.USER_AGENT,
            },
        )
        self.raw_html = res.content.decode("utf-8")

    async def parse_html(self, html: str):
        logger.info("Parsing HTML...")
        self.soup = BeautifulSoup(html, features="lxml")

    def get_name(self) -> str:
        s = self.soup.find("div", {"class": "brand-line__container"})
        brand_name = ""

        if (s_brand := s.find("a", {"class": "brand-line"})) is not None:
            brand_name = f"{s_brand.text} "

        product_name = s.find("span", {"class": "header-name"}).text
        return f"{brand_name}{product_name}"

    def get_image(self) -> str:
        return self.soup.find("img", {"class": "image swiper-lazy"}).get(
            "data-lazy-src"
        )

    def get_variants(self) -> list[dict[str, Any]]:
        out = []
        for s in self.soup.find_all("div", {"class": "product-detail__variant-row"}):
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

    def get_labels(self) -> list[str]:
        if (s_label := self.soup.find("div", {"class": "product-labels"})) is not None:
            return [
                s.text
                for s in s_label.find_all("span", {"class": "product-label__name"})
            ]

        return []

    def get_properties(self) -> list[dict[str, str]]:
        return [
            {
                "key": s.find_all("span")[0].text,
                "value": s.find_all("span")[1].text,
            }
            for s in self.soup.find(
                "div", {"data-testid": "product-detail-info__classifications"}
            ).find_all("div")
        ]

    def get_code(self) -> str:
        properties = self.get_properties()
        return next(p["value"] for p in properties if p["key"].lower() == "art-nr.")

    def get_description(self) -> str:
        return self.soup.find(
            "div", {"class": "truncate product-details__description"}
        ).text

    def get_ratings(self) -> dict[str, Any]:
        rating_block = self.soup.find("span", {"class": "ratings-info"}).text.replace(
            "\xa0", " "
        )
        return {
            "avg_rating": re.search(r"^\d+\.\d+", rating_block, flags=re.I).group(),
            "total_ratings": re.search(r"\(\d+\)$", rating_block, flags=re.I)
            .group()
            .strip("()"),
        }

    def get_number_of_pages(self) -> str:
        return re.search(
            r"\d+$",
            self.soup.find("div", {"class": "pagination-title"}),
            flags=re.I,
        ).group()

    async def get_ean(self) -> str | None:
        api = DouglasAPI()
        product = await api.product.get(self.get_code())
        return product.ean
