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

## Usage

### Web API

Explore the [Swagger UI](https://douglas-crawler-api-lhebzk57ca-ew.a.run.app/api/docs).

Here you will find 3 useful endpoints:

- `/api/crawl` - Crawl a specific product page on [douglas.de](https://www.douglas.de)
- `/api/products`
- `/api/products/{ean}`

### CLI

#### Prerequisites

- [Mise](https://mise.jdx.dev)
- [Docker](https://www.docker.com)

#### Setup

1. Install prerequisites.
2. Install additional prerequisites
    ```shell
    # This will automatically install Python, Poetry, Task, and Terraform.
    # You may not want to use Mise if you already have these tools installed or if
    # you use a different environment manager.
    mise install
    ```
3. Copy the contents of `.env.example` into a new file `.env` in the same directory, and fill in the necessary
   environment variables.
4. Launch Docker containers
    ```shell
    task
    ```

#### Running

Run the crawler

```shell
task crawl
```

The crawler script has a `-u`/`--url` parameter which defaults to
this [category page](https://www.douglas.de/de/c/gesicht/gesichtsmasken/feuchtigkeitsmasken/120308). To use a different
category page:

```shell
task crawl -- -u https://www.douglas.de/<other-page>
```

A local copy of the web API is available at http://localhost:8000/api/docs.
