from math import ceil

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from douglas.db import aget_db
from douglas.internal.crawler import DouglasCrawler, DouglasCrawlerArgs
from douglas.models import Product
from douglas.schemas import (
    Paginated,
    Product as ProductSchema,
)
from douglas.settings import settings

app = FastAPI(
    title="Douglas Crawler API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)


@app.get("/api/health", tags=["core"])
async def health_check():
    return "ok"


@app.post("/api/crawl", response_model=ProductSchema, tags=["product"])
async def crawl_url(body: DouglasCrawlerArgs):
    if body.url.host != settings.BASE_URL.host:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Please use the base URL of www.douglas.de when using this API",
                "expected": settings.BASE_URL.host,
                "got": body.url.host,
            },
        )

    crawl = DouglasCrawler()
    return await crawl.product.get(body.url)


@app.get("/api/products", response_model=Paginated[ProductSchema], tags=["product"])
async def list_products(
    db: AsyncSession = Depends(aget_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
):
    products = await db.scalars(
        select(Product)
        .options(selectinload(Product.classifications), selectinload(Product.variants))
        .limit(page_size)
        .offset((page - 1) * page_size)
    )
    count = await db.scalar(select(func.count()).select_from(Product))

    return {
        "page": page,
        "page_size": page_size,
        "total_pages": ceil(count / page_size),
        "items": products.all(),
    }


@app.get("/api/products/{ean}", response_model=ProductSchema, tags=["product"])
async def get_product(ean: str, db: AsyncSession = Depends(aget_db)):
    res = await db.scalar(
        select(Product)
        .options(selectinload(Product.classifications), selectinload(Product.variants))
        .where(Product.ean == ean)
    )

    if res is None:
        raise HTTPException(
            detail=f"Product with {ean=} not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return res
