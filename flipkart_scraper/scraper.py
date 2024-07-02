import logging
from time import sleep
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Tag
from models import Product, Review

SORT_ORDERS = [
    "MOST_RECENT",
    "POSITIVE_FIRST",
    "NEGATIVE_FIRST",
    "MOST_HELPFUL",
]


class Scraper:
    product: Product

    def __init__(self, product: Product) -> None:
        self.product = product

    def parse_review_div(self, review_div: Tag) -> Review | None:
        containers: list[Tag] = (
            review_div.findChild("div")
            .findChild("div")
            .findChild("div")
            .findChildren("div", recursive=False)
        )

        rating = int(containers[0].findChild("div").text.strip())
        title = str(containers[0].findChild("p").text)

        raw_content = str(containers[1].text)

        text = " ".join(
            raw_content.replace("READ MORE", "").strip().replace(r"\s+", " ").split()
        )

        return Review(
            title=title,
            text=text,
            rating=rating,
            category="routers",
            product_name=self.product.name,
            product_link=self.product.link,
        )

    def scrape_page(self, url: str) -> tuple[list[Review], bool]:
        res: list[Review] = []
        resp = requests.get(url)
        if resp.status_code != 200:
            logging.error(f"Failed to get: {url}")
            return [], False

        doc = BeautifulSoup(resp.content, "html.parser")

        reviews_container = doc.select_one("div.col-9-12")
        if reviews_container is None or len(reviews_container) <= 3:
            logging.error("Couldn't find reviews container")
            return [], False

        review_divs = list(reviews_container.findChildren(recursive=False))[2:-1]
        for div in review_divs:
            try:
                data = self.parse_review_div(div)
                if data is not None:
                    res.append(data)
            except Exception:
                logging.error("Couldn't Parse Review Div")

        return res, True

    def scrape_product(self) -> list[Review]:
        logging.info(f"========= Starting {self.product.name} =========")

        reviews: list[Review] = []

        for sort_order in SORT_ORDERS:
            logging.info(f">>> {sort_order} List")

            has_next_page = True
            current_page = 1
            while has_next_page and len(reviews) < 500:
                url = urljoin(
                    "https://www.flipkart.com",
                    urlparse(self.product.link).path.replace(
                        "/p/", "/product-reviews/"
                    ),
                )
                url += f"?sortOrder={sort_order}"
                if current_page > 1:
                    url += f"&page={current_page}"

                page_reviews, has_next_page = self.scrape_page(url)
                logging.info(f"Got {len(page_reviews)} reviews in page {current_page}")
                reviews.extend(page_reviews)
                sleep(0.05)
                current_page += 1

        logging.info(f"Got total {len(reviews)} reviws.")
        return reviews
