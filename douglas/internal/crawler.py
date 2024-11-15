from httpx import AsyncClient
from pydantic import AnyHttpUrl, BaseModel


class DouglasCrawlerArgs(BaseModel):
    url: AnyHttpUrl


class DouglasCrawler:
    client = AsyncClient()
    user_agent = (
        "Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0"
    )

    def __init__(self, args: DouglasCrawlerArgs):
        self.url = str(args.url)

    async def __call__(self, *args, **kwargs):
        pass

    async def get_raw_html(self):
        _ = await self.client.get(
            self.url,
            headers={
                "Accept": "text/html",
                "User-Agent": self.user_agent,
            },
        )
