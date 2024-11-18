import asyncio
import json
from argparse import ArgumentParser

from httpx import AsyncClient
from tqdm.asyncio import tqdm

from douglas.internal.douglas_api import DouglasAPI, DouglasAPIArgs
from douglas.settings import settings

JSON_DUMP_PARAMS = {
    "indent": 2,
    "ensure_ascii": False,
}

NUM_THREADS = 4


async def main(args: DouglasAPIArgs):
    async with AsyncClient(**DouglasAPI.default_client_params) as client:
        api = DouglasAPI(client=client)
        data = await api.product.search_in_category(
            args.category_code,
            page=args.page,
            page_size=args.page_size,
        )
        out = [d.model_dump(mode="json") for d in data]

        with open(
            settings.BASE_DIR / "outputs" / f"products-{args.page:02}.json", "w+"
        ) as fh:
            json.dump(out, fh, **JSON_DUMP_PARAMS)

        res = []
        with tqdm(total=len(data)) as pbar:
            for d in data:
                res.append(await api.product.get(d.code))
                pbar.update()
        out = [d.model_dump(mode="json") for d in res]

        with open(
            settings.BASE_DIR / "outputs" / f"product-details-{args.page:02}.json", "w+"
        ) as fh:
            json.dump(out, fh, **JSON_DUMP_PARAMS)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-c", "--category-code", type=str)
    parser.add_argument("-p", "--page", type=int, default=1)
    parser.add_argument("-s", "--page-size", type=int, default=50)
    args = DouglasAPIArgs.model_validate(parser.parse_args())

    asyncio.run(main(args))
