from datetime import datetime

from sqlalchemy.orm import relationship

from .conf import base

from sqlalchemy import (  # isort:skip
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)


class User(base):
    telegram_id = Column(Integer)
    name = Column(String(length=255))

    # relation
    links = relationship("Link", lazy="joined", back_populates="user")
    bank = relationship("Bank", lazy="joined", back_populates="user")


class Bank(base):
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float, default=0)
    date = Column(DateTime, default=datetime.now)

    # relation
    user = relationship("User", lazy="joined", back_populates="bank")


class ProductCategory(base):
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(length=255))

    # relation
    products = relationship("Product", lazy="joined", back_populates="category")


class Product(base):
    category_id = Column(Integer, ForeignKey("productcategories.id"))
    name = Column(String(length=255), default="No name")
    price = Column(Float, default=0)
    location = Column(Text, nullable=True)
    date = Column(DateTime, default=datetime.now)

    # relation
    category = relationship("ProductCategory", lazy="joined", back_populates="products")


class LinkCategory(base):
    name = Column(String(length=255))

    # relation
    links = relationship("Link", lazy="joined", back_populates="category")


class Link(base):
    user_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("linkcategories.id"))
    link = Column(String(length=255))

    # relation
    user = relationship("User", lazy="joined", back_populates="links")
    category = relationship("LinkCategory", lazy="joined", back_populates="links")


class CurrencyRate(base):
    name = Column(String(length=255))
    rate_to_kz = Column(Float)


class GmailLetter(base):
    history_id = Column(String(length=500), nullable=False)
