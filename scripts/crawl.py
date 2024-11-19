import asyncio
import json
import os
from argparse import ArgumentParser

from httpx import AsyncClient
from pydantic import AnyHttpUrl
from tqdm.asyncio import tqdm

from douglas.internal.crawler import DouglasCrawler, DouglasCrawlerArgs
from douglas.schemas import Product
from douglas.settings import settings


async def main(args: DouglasCrawlerArgs):
    async with AsyncClient() as client:
        crawl = DouglasCrawler(client)
        data = await crawl.product.search(args.url)

        os.makedirs(settings.BASE_DIR / "outputs/crawl", exist_ok=True)

        with open(settings.BASE_DIR / "outputs/crawl" / "products.json", "w+") as fh:
            json.dump(data.items, fh, indent=2, ensure_ascii=False)

        out: list[Product] = await tqdm.gather(
            *[
                crawl.product.get(
                    str(
                        AnyHttpUrl.build(
                            scheme=settings.BASE_URL.scheme,
                            host=settings.BASE_URL.host,
                            path=p,
                        )
                    )
                )
                for p in data.items
            ],
        )

    with open(settings.BASE_DIR / "outputs/crawl" / "product-details.json", "w+") as fh:
        json.dump(
            [o.model_dump(mode="json") for o in out],
            fh,
            indent=2,
            ensure_ascii=False,
        )


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-u", "--url", type=str)
    args = DouglasCrawlerArgs.model_validate(parser.parse_args())

    asyncio.run(main(args))
