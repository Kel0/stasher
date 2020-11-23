import datetime
import logging
from typing import Dict, List, Optional, Union

import requests
from bs4 import BeautifulSoup as bs
from sqlalchemy.orm import Session

from settings import YANDEX_LOCATION_PNG_LINK
from stasher.database.conf import session

from stasher.database.models import (  # isort:skip
    Bank,
    CurrencyRate,
    GmailLetter,
    Product,
    ProductCategory,
    User,
)

logger = logging.getLogger(__name__)


def de_emojify(input_string):
    return input_string.encode("ascii", "ignore").decode("ascii")


async def create_user(user: Dict[str, str]) -> Union[User, bool]:
    sqlalchemy_session: Session = session()

    _user: List[User] = (
        sqlalchemy_session.query(User)
        .filter(User.telegram_id == user["telegram_id"])
        .all()
    )

    if len(_user) > 0:
        return False

    try:
        sqlalchemy_session.add(User(telegram_id=user["telegram_id"], name=user["name"]))
        sqlalchemy_session.commit()

        _user = (
            sqlalchemy_session.query(User)
            .filter(User.telegram_id == user["telegram_id"])
            .all()
        )
        return _user[0]

    except Exception as e_info:
        logger.error(e_info)
        return False


async def get_costs_by_category(
    user: Dict[str, str], category: str, period: Optional[str] = None
):
    sqlalchemy_session: Session = session()

    _user: List[User] = (
        sqlalchemy_session.query(User)
        .filter(User.telegram_id == user["telegram_id"])
        .all()
    )

    _category: List[ProductCategory] = []
    if period is None and period != "all":
        _category = (
            sqlalchemy_session.query(ProductCategory)
            .filter(ProductCategory.user_id == _user[0].id)  # noqa
            .filter(ProductCategory.name == category)
            .all()
        )

    elif period is not None and period == "all":
        _category = (
            sqlalchemy_session.query(ProductCategory)
            .filter(ProductCategory.user_id == _user[0].id)  # noqa
            .filter(ProductCategory.name == category)
            .all()
        )
        if len(_category) == 0:
            return None

        return _category[0].products

    elif period is not None and period != "all":
        current_day = datetime.datetime.now()
        destination_day = datetime.datetime.now()

        if period == "week":
            destination_day = current_day - datetime.timedelta(days=7)
        elif period == "month":
            destination_day = current_day - datetime.timedelta(days=31)

        _category = (
            sqlalchemy_session.query(ProductCategory)
            .filter(ProductCategory.user_id == _user[0].id)  # noqa
            .filter(ProductCategory.name == category)
            .all()
        )
        _products = (
            sqlalchemy_session.query(Product)
            .filter(Product.category_id == _category[0].id)
            .filter(Product.date.between(destination_day, current_day))
            .all()
        )
        return _products

    return _category[0]


async def create_cost(cost: Dict[str, Union[str, int]]) -> Optional[bool]:
    sqlalchemy_session: Session = session()
    usd = get_current_currency_rate(currency="USD")

    try:
        sqlalchemy_session.add(
            Product(
                category_id=cost["category_id"],
                name=cost["name"],
                price=float(cost["price"]) / usd,
                location=cost["location"],
            )
        )
        sqlalchemy_session.commit()
        return True

    except Exception as e_info:
        logger.error(e_info)
        return None


async def get_costs_by_period(period: str):
    start = datetime.datetime.now()
    end = None

    if period == "week":
        end = start + datetime.timedelta(days=7)
    elif period == "month":
        end = start + datetime.timedelta(days=30)

    if end is None:
        costs: List


async def get_products_categories(
    user: Dict[str, str]
) -> Optional[List[ProductCategory]]:
    sqlalchemy_session: Session = session()

    try:
        _user: List[User] = (
            sqlalchemy_session.query(User)
            .filter(User.telegram_id == user["telegram_id"])
            .all()
        )

        temp_user: Optional[User] = None

        if len(_user) == 0:
            temp_user = await create_user(user=user)
        elif len(_user) > 0:
            temp_user = _user[0]

        if temp_user is None:
            return None

        categories: List[ProductCategory] = (
            sqlalchemy_session.query(ProductCategory)
            .filter(ProductCategory.user_id == temp_user.id)  # noqa
            .all()
        )

        return categories
    except Exception as e_info:
        logger.error(e_info)
        return None


async def add_product_category(name: str, user: Dict[str, str]) -> bool:
    sqlalchemy_session: Session = session()

    try:
        _user: List[User] = (
            sqlalchemy_session.query(User)
            .filter(User.telegram_id == user["telegram_id"])
            .all()
        )

        temp_user: Optional[User] = None

        if len(_user) == 0:
            temp_user = await create_user(user=user)
        elif len(_user) > 0:
            temp_user = _user[0]

        if temp_user is None:
            return False

        sqlalchemy_session.add(ProductCategory(name=name, user_id=temp_user.id))  # noqa
        sqlalchemy_session.commit()
        return True

    except Exception as e_info:
        logger.error(e_info)
        return False


async def add_bank(bank: int, user: Dict[str, str]) -> bool:
    sqlalchemy_session: Session = session()
    currency = get_current_currency_rate(currency="USD")

    try:
        temp_user: User
        _user: List[User] = (
            sqlalchemy_session.query(User)
            .filter(User.telegram_id == user["telegram_id"])
            .all()
        )

        if len(_user) == 0:
            temp_user = await create_user(user=user)
        elif len(_user) > 0:
            temp_user = _user[0]

        sqlalchemy_session.add(
            Bank(
                user_id=temp_user.id,  # noqa,
                amount=float(bank) / currency,
            )
        )
        sqlalchemy_session.commit()
        return True

    except Exception as e_info:
        logger.error(e_info)
        return False


def save_currency(rate: float):
    sqlalchemy_session: Session = session()

    try:
        sqlalchemy_session.add(CurrencyRate(name="USD", rate_to_kz=rate))
        sqlalchemy_session.commit()
    except Exception as e_info:
        logger.error(e_info)


def get_current_currency_rate(currency: str) -> float:
    sqlalchemy_session: Session = session()

    rate: List[CurrencyRate] = (
        sqlalchemy_session.query(CurrencyRate)
        .filter(CurrencyRate.name == currency)
        .all()
    )

    if len(rate) == 0:
        return 1

    return rate[0].rate_to_kz


def scrape_current_amount_of_usd() -> float:
    resp = requests.get(
        url="https://ru.investing.com/currencies/usd-kzt",
        headers={
            "access": "*/*",
            "user-agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/86.0.4240.111 Safari/537.36"
            ),
        },
    )

    if resp.status_code == 200:
        soup = bs(resp.content, "lxml")

        currency = float(
            soup.find("span", attrs={"id": "last_last"}).text.strip().replace(",", ".")
        )
        logger.info(f"USD = {currency}")
        return currency
    else:
        logger.warning("Failed to load scrape page | USD = 425")
        return 425


def construct_location_link(location: Dict[str, float]) -> str:
    link: str = str(YANDEX_LOCATION_PNG_LINK).format(
        lat=location["latitude"], lng=location["longitude"]
    )
    return link


def save_card_costs(history_id: int) -> Optional[bool]:
    sqlalchemy_session: Session = session()

    gmail: List[GmailLetter] = (
        sqlalchemy_session.query(GmailLetter)
        .filter(GmailLetter.history_id == history_id)
        .all()
    )
    if len(gmail) > 0:
        return None

    try:
        sqlalchemy_session.add(GmailLetter(history_id=history_id))
        sqlalchemy_session.commit()
        return True
    except Exception as e_info:
        logger.error(e_info)
        return None
