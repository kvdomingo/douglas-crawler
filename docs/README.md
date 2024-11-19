# douglas-crawler

## Objectives

- Collects all product links from this
  specific [category page](https://www.douglas.de/de/c/gesicht/gesichtsmasken/feuchtigkeitsmasken/120308). It should
  traverse all available pages for this link. Note: The total amount of pages might change over time.
- Collects all product information which is marked in red (image above) from the links you have collected from the
  category page. The information must be extracted via HTML source code. Use any HTML/XML parsing library of your
  choice. e.g. Beautifulsoup
- Gets the unique product id `ean`. This id might not visible in the html source code and can get be only accessed via
  request interception/https sniffing of the product page. TIP:
  For [this product](https://www.douglas.de/de/p/3001055831) you should get `ean=3605971937811`.
- Store all crawled information in a postgres database. Use the free tier of [Supabase](https://supabase.com/).

## Running locally

### Prerequisites

- [Docker](https://www.docker.com)

### Setup

1. Install prerequisites.
2. Install additional prerequisites
    ```shell
    mise install
    ```
3. Launch Docker containers
    ```shell
    task
    ```
4. Run the crawler
    ```shell
    task crawl -- -u https://www.douglas.de/de/c/gesicht/gesichtsmasken/feuchtigkeitsmasken/120308
    ```
