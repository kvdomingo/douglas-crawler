import asyncio
from argparse import ArgumentParser

from douglas.internal.crawler import DouglasCrawler, DouglasCrawlerArgs

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-u", "--url", type=str)
    args = parser.parse_args()

    crawl = DouglasCrawler(DouglasCrawlerArgs.model_validate(args))
    data = asyncio.run(crawl())
    print(data.model_dump_json(indent=2))
