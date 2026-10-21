
######################################################################
# Copyright 2016, 2022 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
######################################################################

"""
Product Store Service with UI
"""

from flask import jsonify, request, abort
from flask import url_for  # noqa: F401
from service.models import Product, DataValidationError
from service.common import status
from . import app


@app.route("/health")
def healthcheck():
    """Health check."""
    return jsonify(status=200, message="OK"), status.HTTP_200_OK


@app.route("/")
def index():
    """Serve the home page."""
    return app.send_static_file("index.html")


def check_content_type(content_type):
    """Validate request content type."""
    if request.headers.get("Content-Type") != content_type:
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            description=f"Content-Type must be {content_type}",
        )


@app.route("/products", methods=["POST"])
def create_products():
    """Create a product."""
    check_content_type("application/json")
    data = request.get_json(silent=True)

    if not data:
        abort(status.HTTP_400_BAD_REQUEST, description="Invalid JSON body")

    try:
        product = Product()
        product.deserialize(data)
        product.create()
    except (DataValidationError, ValueError, TypeError) as error:
        abort(status.HTTP_400_BAD_REQUEST, description=str(error))

    location_url = url_for(
        "get_products", product_id=product.id, _external=True
    )
    return (
        jsonify(product.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


@app.route("/products", methods=["GET"])
def list_products():
    """List all products."""
    products = Product.all()
    results = [product.serialize() for product in products]
    return jsonify(results), status.HTTP_200_OK


@app.route("/products/<int:product_id>", methods=["GET"])
def get_products(product_id):
    """Read a product by ID."""
    product = Product.find(product_id)

    if product is None:
        abort(status.HTTP_404_NOT_FOUND, description="Product not found")

    return jsonify(product.serialize()), status.HTTP_200_OK


@app.route("/products/<int:product_id>", methods=["PUT"])
def update_products(product_id):
    """Update an existing product."""
    check_content_type("application/json")

    product = Product.find(product_id)
    if product is None:
        abort(status.HTTP_404_NOT_FOUND, description="Product not found")

    data = request.get_json(silent=True)
    if not data:
        abort(status.HTTP_400_BAD_REQUEST, description="Invalid JSON body")

    try:
        product.deserialize(data)
        product.update()
    except (DataValidationError, ValueError, TypeError) as error:
        abort(status.HTTP_400_BAD_REQUEST, description=str(error))

    return jsonify(product.serialize()), status.HTTP_200_OK


@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_products(product_id):
    """Delete a product by ID."""
    product = Product.find(product_id)

    if product is None:
        abort(status.HTTP_404_NOT_FOUND, description="Product not found")

    product.delete()
    return "", status.HTTP_204_NO_CONTENT
