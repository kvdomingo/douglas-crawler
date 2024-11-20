from loguru import logger

from douglas.internal.crawler import DouglasCrawlerArgs


async def main(args: DouglasCrawlerArgs):
    import polars as pl
    from httpx import AsyncClient, AsyncHTTPTransport
    from pydantic import AnyHttpUrl
    from sqlalchemy.dialects.postgresql import insert
    from tqdm.asyncio import tqdm

    from douglas.db import aget_db_context
    from douglas.internal.crawler import DouglasCrawler
    from douglas.models import Product, ProductClassification, ProductVariant
    from douglas.schemas import Product as ProductSchema
    from douglas.settings import settings

    transport = AsyncHTTPTransport(retries=10, http2=True)

    async with AsyncClient(timeout=10, transport=transport) as client:
        crawl = DouglasCrawler(client)
        data = await crawl.product.search(args.url)
        errors = []

        products: list[ProductSchema] = []
        coros = [
            crawl.product.get(
                str(
                    AnyHttpUrl.build(
                        scheme=settings.BASE_URL.scheme,
                        host=settings.BASE_URL.host,
                        path=p.lstrip("/"),
                    )
                )
            )
            for p in data.items
        ]
        for coro in tqdm.as_completed(coros):
            products.append(await coro)

        logger.debug(errors)
        products = [p for p in products if not isinstance(p, Exception)]

        df = pl.from_dicts([p.model_dump(mode="json") for p in products]).unique(
            ["ean"], keep="first"
        )
        variants_df = (
            df.select("variants", product_id=pl.col("ean"))
            .explode("variants")
            .unnest("variants")
        )
        classifications_df = (
            df.select("classifications", product_id=pl.col("ean"))
            .explode("classifications")
            .unnest("classifications")
        )

        async with aget_db_context() as db:
            product_cols: list[str] = Product.__table__.columns.keys()
            product_insert_stmt = insert(Product)
            await db.execute(
                product_insert_stmt.on_conflict_do_update(
                    "pk_products",
                    set_={
                        c: getattr(product_insert_stmt.excluded, c)
                        for c in product_cols
                        if c != "ean"
                    },
                ),
                df.to_dicts(),
            )

            product_variant_cols: list[str] = ProductVariant.__table__.columns.keys()
            variant_insert_stmt = insert(ProductVariant)
            await db.execute(
                variant_insert_stmt.on_conflict_do_update(
                    "uq_product_variants_product_id_name",
                    set_={
                        c: getattr(variant_insert_stmt.excluded, c)
                        for c in product_variant_cols
                        if c not in ["product_id", "name"]
                    },
                ),
                variants_df.to_dicts(),
            )

            product_classification_cols: list[str] = (
                ProductClassification.__table__.columns.keys()
            )
            classification_insert_stmt = insert(ProductClassification)
            await db.execute(
                classification_insert_stmt.on_conflict_do_update(
                    "uq_product_classifications_product_id_key",
                    set_={
                        c: getattr(classification_insert_stmt.excluded, c)
                        for c in product_classification_cols
                        if c not in ["product_id", "key"]
                    },
                ),
                classifications_df.to_dicts(),
            )

            await db.commit()


if __name__ == "__main__":
    import asyncio
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument(
        "-u",
        "--url",
        type=str,
        help="Douglas URL of a specific category page",
        default="https://www.douglas.de/de/c/gesicht/gesichtsmasken/feuchtigkeitsmasken/120308",
    )
    args = DouglasCrawlerArgs.model_validate(parser.parse_args())

    asyncio.run(main(args))
