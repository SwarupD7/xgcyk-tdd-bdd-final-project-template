
# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
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

"""Test cases for Product Model."""

import os
import logging
import unittest
from decimal import Decimal

from service.models import Product, Category, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI",
    "postgresql://postgres:postgres@localhost:5432/postgres",
)


######################################################################
# PRODUCT MODEL TEST CASES
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model."""

    @classmethod
    def setUpClass(cls):
        """Run once before the entire test suite."""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Run once after the entire test suite."""
        db.session.close()

    def setUp(self):
        """Run before each test."""
        db.session.query(Product).delete()
        db.session.commit()

    def tearDown(self):
        """Run after each test."""
        db.session.remove()

    def test_create_a_product(self):
        """It should create a product and assert that it exists."""
        product = Product(
            name="Fedora",
            description="A red hat",
            price=12.50,
            available=True,
            category=Category.CLOTHS,
        )
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertIsNotNone(product)
        self.assertIsNone(product.id)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertTrue(product.available)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should create a product and add it to the database."""
        self.assertEqual(Product.all(), [])

        product = ProductFactory()
        product.id = None
        product.create()

        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)

        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_read_a_product(self):
        """It should read a product."""
        product = ProductFactory()
        product.id = None
        product.create()

        found_product = Product.find(product.id)

        self.assertIsNotNone(found_product)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(Decimal(found_product.price), product.price)

    def test_update_a_product(self):
        """It should update a product."""
        product = ProductFactory()
        product.id = None
        product.create()

        original_id = product.id
        product.description = "testing"
        product.update()

        updated_product = Product.find(original_id)
        self.assertIsNotNone(updated_product)
        self.assertEqual(updated_product.id, original_id)
        self.assertEqual(updated_product.description, "testing")

    def test_delete_a_product(self):
        """It should delete a product."""
        product = ProductFactory()
        product.id = None
        product.create()

        self.assertEqual(len(Product.all()), 1)
        product.delete()

        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """It should list all products."""
        self.assertEqual(len(Product.all()), 0)

        for _ in range(5):
            product = ProductFactory()
            product.id = None
            product.create()

        self.assertEqual(len(Product.all()), 5)

    def test_find_by_name(self):
        """It should find products by name."""
        names = [
            "Test Product",
            "Test Product",
            "Test Product",
            "Other Product",
            "Another Product",
        ]

        for name in names:
            product = ProductFactory(name=name)
            product.id = None
            product.create()

        found_products = Product.find_by_name("Test Product")

        self.assertEqual(len(found_products), 3)
        for product in found_products:
            self.assertEqual(product.name, "Test Product")

    def test_find_by_category(self):
        """It should find products by category."""
        categories = [
            Category.FOOD,
            Category.FOOD,
            Category.FOOD,
            Category.FOOD,
            Category.FOOD,
            Category.CLOTHS,
            Category.UNKNOWN,
            Category.TOOLS,
            Category.HOUSEWARES,
            Category.AUTOMOTIVE,
        ]

        for category in categories:
            product = ProductFactory(category=category)
            product.id = None
            product.create()

        found_products = Product.find_by_category(Category.FOOD)

        self.assertEqual(len(found_products), 5)
        for product in found_products:
            self.assertEqual(product.category, Category.FOOD)

    def test_find_by_availability(self):
        """It should find products by availability."""
        availability_values = [
            True, True, True, True, True,
            True, False, False, False, False,
        ]

        for available in availability_values:
            product = ProductFactory(available=available)
            product.id = None
            product.create()

        expected_count = availability_values.count(True)
        found_products = Product.find_by_availability(True)

        self.assertEqual(len(found_products), expected_count)
        for product in found_products:
            self.assertTrue(product.available)
