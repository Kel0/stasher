import json
from typing import List

from telegraph import Telegraph

from .database.models import Product
from .utils import construct_location_link


def create_telegraph(products: List[Product], period) -> str:
    telegraph = Telegraph()
    telegraph.create_account(short_name="Stasher")
    html_content: str = ""
    total: float = 0

    for index, product in enumerate(products):
        location = product.location
        if "{" in product.location and "}" in product.location:
            _location = construct_location_link(location=json.loads(product.location))
            location = f"<a href='{_location}'>Link to location image</a>"

        html_content += (
            f"<p>№ {index + 1}</p>"
            f"<p>Name: {product.name}</p>"
            f"<p>Price: {round(product.price, 2)}$</p>"
            f"<p>Date: {product.date} </p>"
            f"<p>Location: {location}</p><br><br>"
        )
        total += product.price

    html_content += "<hr>"
    html_content += f"<p style='text-align: center'>Total costs: {round(total, 2)}$</p>"
    page = telegraph.create_page(
        title="All costs" if period == "all" else f"1 {period}",
        html_content=html_content,
    )

    return page["url"]
