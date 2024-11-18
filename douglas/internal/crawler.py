import re
from typing import Any

from bs4 import BeautifulSoup
from httpx import AsyncClient, AsyncHTTPTransport
from loguru import logger
from pydantic import AnyHttpUrl

from douglas.schemas import BaseModel, Product, ProductClassification, ProductVariant


class DouglasCrawlerArgs(BaseModel):
    url: AnyHttpUrl


class DouglasCrawler:
    transport = AsyncHTTPTransport(retries=3, http2=True)
    client = AsyncClient(transport=transport)
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
        return Product(
            url=self.url,
            ean=None,
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
        return self.soup.find("span", {"class": "header-name"}).text

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
                obj["original_price"] = (
                    re.search(
                        r"\d+\.\d+", s_price_original.text.replace(",", "."), flags=re.I
                    ).group(),
                )

            out.append(obj)

        return out

    def get_labels(self) -> list[str]:
        return [
            s.text
            for s in self.soup.find("div", {"class": "product-labels"}).find_all(
                "span", {"class": "product-label__name"}
            )
        ]

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
