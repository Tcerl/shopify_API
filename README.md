# shopify_API

Overview

This Python script provides automation for managing Shopify store data, including creating, updating, and deleting resources such as products, collections, customers, and orders using the Shopify API.

Features

Create

Smart Collections

Custom Collections

Products (with and without options)

Customers

Orders for customers

Update

Product details (price, images, quantity, etc.)

Product variants

Product publication status

Delete

All created data including orders, products, collections, and customers

Prerequisites

Requirements

Python 3.x

requests library

Install dependencies using:

pip install requests

Shopify API Credentials

You need to set up your STORE_URL and ACCESS_TOKEN before running the script:

STORE_URL = "your-shopify-store.myshopify.com"
ACCESS_TOKEN = "your-access-token"

Setup and Usage

Load the script and update the STORE_URL and ACCESS_TOKEN.

Run the script:

python script.py

Select an operation from the menu:

1 Create Shopify resources (collections, products, customers, orders)

2 Update all products and variants

3 Delete all created data

4 Exit the script

Utility Functions

shopify_request(method, endpoint, payload=None): Handles API requests.

load_data(filename): Loads JSON data for API requests.

save_data(data, filename): Saves API response data.

API Endpoints Used

/admin/api/2025-01/products.json

/admin/api/2025-01/custom_collections.json

/admin/api/2025-01/smart_collections.json

/admin/api/2025-01/customers.json

/admin/api/2025-01/orders.json

/admin/api/2025-01/inventory_levels/set.json

Notes

Ensure you have proper API permissions for the Shopify store.

The script logs API responses for debugging purposes.

It uses JSON files to store API responses for better traceability.

License

This project is licensed under the MIT License.

