import asyncio
from argparse import ArgumentParser

from douglas.internal.crawler import DouglasCrawler, DouglasCrawlerArgs


async def main(args: DouglasCrawlerArgs):
    crawl = DouglasCrawler(args)
    data = await crawl()
    print(data.model_dump_json(indent=2))


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-u", "--url", type=str)
    args = DouglasCrawlerArgs.model_validate(parser.parse_args())

    asyncio.run(main(args))
