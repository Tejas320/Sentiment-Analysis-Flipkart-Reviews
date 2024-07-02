import csv
import logging
from typing import Any, Generator

from models import Product
from scraper import Scraper

logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)


def load_product_links(file_name: str) -> Generator[Product, Any, Any]:
    with open(file_name, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            yield Product(name=row[0], link=row[1])


def main() -> None:
    reviews: list[list[Any]] = []
    product_links = list(load_product_links("./data/product_links.csv"))

    for product in product_links:
        scraper = Scraper(product=product)
        product_reviews = [list(it) for it in scraper.scrape_product()]
        reviews.extend(product_reviews)

    with open("./data/reviews_raw.csv", "w+", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(reviews)


if __name__ == "__main__":
    main()
