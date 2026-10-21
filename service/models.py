
# Copyright 2016, 2023 John Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Models for Product Demo Service.

Product - A product used in the Product Store.
"""

import logging
from decimal import Decimal
from enum import Enum

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# SQLAlchemy object initialized later in init_db()
db = SQLAlchemy()


def init_db(app):
    """Initialize the SQLAlchemy app."""
    Product.init_db(app)


class DataValidationError(Exception):
    """Used for data validation errors when deserializing."""


class Category(Enum):
    """Enumeration of valid Product Categories."""

    UNKNOWN = 0
    CLOTHS = 1
    FOOD = 2
    HOUSEWARES = 3
    AUTOMOTIVE = 4
    TOOLS = 5


class Product(db.Model):
    """Class representing a Product."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    price = db.Column(db.Numeric, nullable=False)
    available = db.Column(db.Boolean(), nullable=False, default=True)
    category = db.Column(
        db.Enum(Category),
        nullable=False,
        server_default=Category.UNKNOWN.name,
    )

    def __repr__(self):
        return f"<Product {self.name} id=[{self.id}]>"

    def create(self):
        """Create a Product in the database."""
        logger.info("Creating %s", self.name)
        self.id = None
        db.session.add(self)
        db.session.commit()

    def update(self):
        """Update a Product in the database."""
        logger.info("Saving %s", self.name)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        db.session.commit()

    def delete(self):
        """Remove a Product from the database."""
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self) -> dict:
        """Serialize a Product into a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": str(self.price),
            "available": self.available,
            "category": self.category.name,
        }

    def deserialize(self, data: dict):
        """Deserialize a dictionary into a Product."""
        try:
            self.name = data["name"]
            self.description = data["description"]
            self.price = Decimal(data["price"])

            if isinstance(data["available"], bool):
                self.available = data["available"]
            else:
                raise DataValidationError(
                    "Invalid type for boolean [available]: "
                    + str(type(data["available"]))
                )

            self.category = getattr(Category, data["category"])

        except AttributeError as error:
            raise DataValidationError(
                "Invalid attribute: " + error.args[0]
            ) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid product: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid product: body of request contained bad or no data "
                + str(error)
            ) from error

        return self

    @classmethod
    def init_db(cls, app: Flask):
        """Initialize the database session."""
        logger.info("Initializing database")
        db.init_app(app)
        app.app_context().push()
        db.create_all()

    @classmethod
    def all(cls) -> list:
        """Return all Products."""
        logger.info("Processing all Products")
        return cls.query.all()

    @classmethod
    def find(cls, product_id: int):
        """Find a Product by ID, or return None if not found."""
        logger.info("Processing lookup for id %s ...", product_id)
        return cls.query.get(product_id)

    @classmethod
    def find_by_name(cls, name: str) -> list:
        """Return all Products with the given name."""
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name).all()

    @classmethod
    def find_by_price(cls, price: Decimal) -> list:
        """Return all Products with the given price."""
        logger.info("Processing price query for %s ...", price)
        price_value = price
        if isinstance(price, str):
            price_value = Decimal(price.strip(' "'))
        return cls.query.filter(cls.price == price_value)

    @classmethod
    def find_by_availability(cls, available: bool = True) -> list:
        """Return all Products by availability."""
        logger.info("Processing available query for %s ...", available)
        return cls.query.filter(cls.available == available).all()

    @classmethod
    def find_by_category(cls, category: Category = Category.UNKNOWN) -> list:
        """Return all Products by Category."""
        logger.info("Processing category query for %s ...", category.name)
        return cls.query.filter(cls.category == category).all()
