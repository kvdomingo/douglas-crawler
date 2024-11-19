from fastapi import FastAPI, HTTPException, status

from douglas.internal.crawler import DouglasCrawler, DouglasCrawlerArgs
from douglas.schemas.product import Product
from douglas.settings import settings

app = FastAPI(
    title="Douglas Crawler API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)


@app.get("/api/health")
async def health_check():
    return "ok"


@app.post("/api/crawl", response_model=Product)
async def crawl_url(body: DouglasCrawlerArgs):
    if body.url.host != settings.BASE_URL.host:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Please use the base URL of www.douglas.de when using this API",
                "expected": settings.BASE_URL.host,
                "got": body.url.host,
            },
        )

    crawl = DouglasCrawler()
    return await crawl.product.get(body.url)
