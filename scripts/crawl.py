from douglas.internal.crawler import DouglasCrawlerArgs


async def main(args: DouglasCrawlerArgs):
    import os

    import polars as pl
    from httpx import AsyncClient
    from pydantic import AnyHttpUrl
    from tqdm.asyncio import tqdm

    from douglas.db import aget_db_context
    from douglas.internal.crawler import DouglasCrawler
    from douglas.models import Product, ProductClassification, ProductVariant
    from douglas.schemas import Product as ProductSchema
    from douglas.settings import settings

    async with AsyncClient() as client:
        crawl = DouglasCrawler(client)
        data = await crawl.product.search(args.url)

        os.makedirs(settings.BASE_DIR / "outputs/crawl", exist_ok=True)

        res: list[ProductSchema] = await tqdm.gather(
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
            ]
        )
        df = pl.from_dicts([r.model_dump(mode="json") for r in res]).unique(
            ["ean"], keep="first"
        )
        products = [
            Product(
                **{
                    **d,
                    "classifications": [
                        ProductClassification(**c) for c in d["classifications"]
                    ],
                    "variants": [ProductVariant(**v) for v in d["variants"]],
                }
            )
            for d in df.to_dicts()
        ]

        async with aget_db_context() as db:
            db.add_all(products)
            await db.commit()


if __name__ == "__main__":
    import asyncio
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument(
        "-u", "--url", type=str, help="Douglas URL of a specific category page"
    )
    args = DouglasCrawlerArgs.model_validate(parser.parse_args())

    asyncio.run(main(args))
