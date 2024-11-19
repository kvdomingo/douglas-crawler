import asyncio
import json
import os
from argparse import ArgumentParser

from httpx import AsyncClient, AsyncHTTPTransport
from tqdm.asyncio import tqdm

from douglas.internal.douglas_api import DouglasAPI, DouglasAPIArgs
from douglas.schemas import DouglasProductDetail
from douglas.settings import settings

JSON_DUMP_PARAMS = {
    "indent": 2,
    "ensure_ascii": False,
}


async def main(args: DouglasAPIArgs):
    transport = AsyncHTTPTransport(retries=3)

    async with AsyncClient(
        **DouglasAPI.default_client_params, transport=transport
    ) as client:
        api = DouglasAPI(client=client)
        data = await api.product.search_in_category(args.category_code, page=args.page)
        out = [d.model_dump(mode="json") for d in data]

        os.makedirs(settings.BASE_DIR / "outputs/api", exist_ok=True)

        with open(
            settings.BASE_DIR / "outputs/api" / f"products-{args.page:02}.json", "w+"
        ) as fh:
            json.dump(out, fh, **JSON_DUMP_PARAMS)

        res: list[DouglasProductDetail] = await tqdm.gather(
            *[api.product.get(d.code) for d in data]
        )
        out = [d.model_dump(mode="json") for d in res]

    with open(
        settings.BASE_DIR / "outputs/api" / f"product-details-{args.page:02}.json",
        "w+",
    ) as fh:
        json.dump(out, fh, **JSON_DUMP_PARAMS)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-c", "--category-code", type=str)
    parser.add_argument("-p", "--page", type=int, default=1)
    parser.add_argument("-s", "--page-size", type=int, default=50)
    args = DouglasAPIArgs.model_validate(parser.parse_args())

    asyncio.run(main(args))
