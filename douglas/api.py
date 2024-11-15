from fastapi import FastAPI

app = FastAPI(
    title="Douglas Crawler API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)


@app.get("/api/health")
async def health():
    return "ok"
