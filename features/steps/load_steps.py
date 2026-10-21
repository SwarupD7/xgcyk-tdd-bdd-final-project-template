
######################################################################
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
######################################################################

"""
Product Steps

Steps file for products.feature.
"""

import requests
from behave import given

HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204


@given('the following products')
def step_impl(context):
    """Delete existing products and load products from the feature table."""
    rest_endpoint = f"{context.base_url}/products"

    # Get all existing products
    context.resp = requests.get(rest_endpoint, timeout=10)
    assert context.resp.status_code == HTTP_200_OK, (
        f"Could not retrieve products: {context.resp.status_code} "
        f"{context.resp.text}"
    )

    # Delete existing products
    for product in context.resp.json():
        context.resp = requests.delete(
            f"{rest_endpoint}/{product['id']}",
            timeout=10,
        )
        assert context.resp.status_code == HTTP_204_NO_CONTENT, (
            f"Could not delete product: {context.resp.status_code} "
            f"{context.resp.text}"
        )

    # Create products from the feature table
    for row in context.table:
        product_data = {
            "name": row["name"],
            "description": row["description"],
            "price": row["price"],
            "available": row["available"].strip().lower() == "true",
            "category": row["category"].strip().upper(),
        }

        context.resp = requests.post(
            rest_endpoint,
            json=product_data,
            timeout=10,
        )

        # Print the actual API response if product creation fails
        print("POST STATUS:", context.resp.status_code)
        print("POST RESPONSE:", context.resp.text)

        assert context.resp.status_code == HTTP_201_CREATED, (
            f"Product creation failed: {context.resp.status_code} "
            f"{context.resp.text}"
        )
