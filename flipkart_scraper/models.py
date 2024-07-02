from dataclasses import asdict, dataclass


@dataclass
class Product:
    name: str
    link: str

    def __iter__(self):
        return iter(asdict(self).values())


@dataclass
class Review:
    title: str
    text: str
    rating: int
    category: str
    product_name: str
    product_link: str

    def __iter__(self):
        return iter(asdict(self).values())
