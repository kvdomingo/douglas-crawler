import asyncio
from argparse import ArgumentParser

from douglas.internal.crawler import DouglasCrawler, DouglasCrawlerArgs

parser = ArgumentParser()
parser.add_argument("-u", "--url", type=str)
args = parser.parse_args()

crawl = DouglasCrawler(DouglasCrawlerArgs.model_validate(args))
asyncio.run(crawl())
