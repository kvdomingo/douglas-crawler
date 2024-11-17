import asyncio
from argparse import ArgumentParser

from douglas.internal.douglas_api import DouglasAPI, DouglasAPIArgs

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-c", "--product-code", type=str)
    args = DouglasAPIArgs.model_validate(parser.parse_args())

    api = DouglasAPI()
    data = asyncio.run(api.product.get(args.product_code))
    print(data.model_dump_json(indent=2))
