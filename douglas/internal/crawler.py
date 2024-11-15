import json
import re
from typing import Any

from bs4 import BeautifulSoup
from httpx import AsyncClient
from loguru import logger
from pydantic import AnyHttpUrl, BaseModel, ConfigDict

from douglas.schemas.product import Product, ProductVariant


class DouglasCrawlerArgs(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    url: AnyHttpUrl


class DouglasCrawler:
    client = AsyncClient()
    user_agent = (
        "Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0"
    )
    soup: BeautifulSoup

    def __init__(self, args: DouglasCrawlerArgs):
        self.url = str(args.url)

    async def __call__(self, *args, **kwargs):
        html = await self.get_raw_html()
        await self.get_parsed_html(html)

        ratings = self.get_ratings()
        product = Product(
            name=self.get_name(),
            image=self.get_image(),
            variant=[ProductVariant.model_validate(v) for v in self.get_variants()],
            product_labels=self.get_product_labels(),
            product_details=self.get_product_details(),
            description=self.get_description(),
            avg_rating=ratings["avg_rating"],
            total_ratings=ratings["total_ratings"],
        )

        logger.debug(
            json.dumps(product.model_dump(mode="json"), indent=2, ensure_ascii=False)
        )
        return product

    async def get_raw_html(self) -> str:
        logger.info(f"Crawling {self.url}...")
        res = await self.client.get(
            self.url,
            headers={
                "Accept": "text/html",
                "Accept-Encoding": "gzip,deflate,br,zstd",
                "Accept-Language": "en-US,en",
                "User-Agent": self.user_agent,
            },
        )
        return res.content.decode("utf-8")

    async def get_parsed_html(self, html: str):
        logger.info("Parsing HTML...")
        self.soup = BeautifulSoup(html, features="lxml")

    def get_name(self) -> str:
        return self.soup.find("span", attrs={"class": "header-name"}).text

    def get_image(self) -> str:
        return self.soup.find("img", attrs={"class": "image swiper-lazy"}).get(
            "data-lazy-src"
        )

    def get_variants(self) -> list[dict[str, Any]]:
        return [
            {
                "name": s.find(
                    "div", attrs={"class": "product-detail__variant-name"}
                ).text,
                "price": re.search(
                    r"\d+\.\d+",
                    s.find("span", attrs={"class": "product-price__price"})
                    .text.replace("\xa0", " ")
                    .replace(",", "."),
                    flags=re.I,
                ).group(),
            }
            for s in self.soup.find_all(
                "div", attrs={"class": "product-detail__variant-row"}
            )
        ]

    def get_product_labels(self) -> list[str]:
        return [
            s.text
            for s in self.soup.find("div", attrs={"class": "product-labels"}).find_all(
                "span", attrs={"class": "product-label__name"}
            )
        ]

    def get_product_details(self) -> dict[str, Any]:
        return {
            s.find_all("span")[0].text: s.find_all("span")[1].text
            for s in self.soup.find(
                "div", attrs={"data-testid": "product-detail-info__classifications"}
            ).find_all("div")
        }

    def get_description(self) -> str:
        return self.soup.find(
            "div", attrs={"class": "truncate product-details__description"}
        ).text

    def get_ratings(self) -> dict[str, Any]:
        rating_block = self.soup.find(
            "span", attrs={"class": "ratings-info"}
        ).text.replace("\xa0", " ")
        return {
            "avg_rating": re.search(r"^\d+\.\d+", rating_block, flags=re.I).group(),
            "total_ratings": re.search(r"\(\d+\)$", rating_block, flags=re.I)
            .group()
            .strip("()"),
        }
