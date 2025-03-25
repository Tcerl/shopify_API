import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

STORE_URL = ""
ACCESS_TOKEN = ""
HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": ACCESS_TOKEN
}

# Utility Functions
def load_data(filename="shopify_data_new.json"):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(data, filename="shopify_data_save_new.json"):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def shopify_request(method, endpoint, payload=None):
    url = f"{STORE_URL}/admin/api/2025-01/{endpoint}"
    response = requests.request(method, url, headers=HEADERS, json=payload)
    
    if response.status_code in [200, 201]:
        return response.json()
    else:
        logging.error(f"Request failed: {response.status_code} - {response.text}")
        return None

def create_resources(resource_type, data_key):
    created_items = []
    for item_data in load_data().get(data_key, []):
        payload = {resource_type: item_data}
        response = shopify_request("POST", f"{resource_type}s.json", payload)
        if response:
            created_items.append(response[resource_type])
    return created_items

def create_orders(customers, products):
    """ Tạo nhiều order """
    orders = []
    for customer in customers:
        for product in products:
            order_data = {
                "order": {
                    "customer": {"id": customer["id"]},
                    "line_items": [{"variant_id": product["variants"][0]["id"], "quantity": 1}]
                }
            }
            response = shopify_request("POST", "orders.json", order_data)
            if response:
                orders.append(response["order"])
    return orders


# def create_order(customer_id, variant_id):
#     order_data = load_data()["order"]
#     order_data["customer"] = {"id": customer_id}
#     order_data["line_items"][0]["variant_id"] = variant_id
#     return shopify_request("POST", "orders.json", {"order": order_data})

# Update Functions
def update_product(product_id, data_key):
    payload = {"product": load_data()[data_key]}
    return shopify_request("PUT", f"products/{product_id}.json", payload)

def update_product_image(product_id, image_url):
    url = f"{STORE_URL}/admin/api/2025-01/products/{product_id}.json"
    
    payload = {
        "product": {
            "id": product_id,
            "images": [{"src": image_url}]
        }
    }
    
    response = requests.put(url, headers=HEADERS, json=payload)
    
    print(f"Response status code: {response.status_code}")
    print(f"Response text: {response.text}")
    
    if response.status_code == 200:
        try:
            result = response.json()
            print("Product image updated successfully:", result)
            return result
        except requests.exceptions.JSONDecodeError:
            print("Error: Response is not valid JSON")
            return None
    else:
        print(f"Error updating product image: {response.status_code}, {response.text}")
        return None


def update_product_status(product_id):
    url = f"{STORE_URL}/admin/api/2025-01/products/{product_id}.json"
    
    payload = {
        "product": {
            "id": product_id,
            "status": "active",
            "published_scope": "global",
            "published_at": "2025-03-21T23:06:25-04:00"
        }
    }
    
    response = requests.put(url, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        print(f"Product {product_id} is now published on Online Store!")
        return True
    else:
        print(f"Failed to publish product {product_id}: {response.text}")
        return False
    

def get_location_id_data():
    url = f"{STORE_URL}/admin/api/2025-01/locations.json"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        locations = response.json().get("locations", [])
        if locations:
            return locations[0]["id"]  # Get the first location
    print("Error getting location ID:", response.text)
    return None

def get_variant_inventory_item_id(variant_id):
    url = f"{STORE_URL}/admin/api/2025-01/variants/{variant_id}.json"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        variant = response.json().get("variant", {})
        return variant.get("inventory_item_id")
    
    print("Error getting variant inventory item ID:", response.text)
    return None

def update_inventory_quantity_data(variant_id):
    location_id = get_location_id_data()
    inventory_item_id = get_variant_inventory_item_id(variant_id)
    
    if not location_id or not inventory_item_id:
        print("Missing required IDs")
        return False

    url = f"{STORE_URL}/admin/api/2025-01/inventory_levels/set.json"
    payload = {
        "location_id": location_id,
        "inventory_item_id": inventory_item_id,
        "available": 30
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        print(f"Successfully updated inventory for variant {variant_id}")
        return True
    
    print(f"Error updating inventory: {response.text}")
    return False

def update_product_variant_data(product_id, variant_id):
    url = f"{STORE_URL}/admin/api/2025-01/products/{product_id}/variants/{variant_id}.json"
    
    update_data = load_data().get("update_product_with_options", {}).get("product", {})
    selected_variant = next((v for v in update_data.get("variants", []) if str(v.get("id")) == str(variant_id)), None)
    update_product_status(product_id)
    print(selected_variant)
    print(url)
    if not selected_variant:
        print("Variant not found in update data!")
        return None
    
    payload = {"variant": selected_variant}  
    response = requests.put(url, headers=HEADERS, json=payload)
    
    print(f"Response status code: {response.status_code}")
    print(f"Response text: {response.text}")
    
    if response.status_code == 200:
        try:
            result = response.json()
            
            if not update_inventory_quantity_data(variant_id):
                print("Failed to update inventory quantity!")
            
            image_url = update_data.get("images", [{}])[0].get("src")
            if image_url:
                if not update_product_image(product_id, image_url):
                    print("Failed to update product image!")
            
            print("Variant updated successfully:", result)
            return result
        except requests.exceptions.JSONDecodeError:
            print("Error: Response is not valid JSON")
            return None
    else:
        print(f"Error updating variant: {response.status_code}, {response.text}")
        return None
    
# Refund Order before Deletion
def refund_order(order_id):
    transactions = shopify_request("GET", f"orders/{order_id}/transactions.json")
    if not transactions or "transactions" not in transactions:
        print(f" No transactions found for order {order_id}.")
        return None

    refund_line_items = []
    order_data = shopify_request("GET", f"orders/{order_id}.json")
    if not order_data or "order" not in order_data:
        print(f" Could not retrieve order {order_id}.")
        return None
    
    for item in order_data["order"].get("line_items", []):
        refund_line_items.append({
            "line_item_id": item["id"],
            "quantity": item["quantity"]
        })
    
    refund_payload = {
        "refund": {
            "order_id": order_id,
            "notify": False,
            "refund_line_items": refund_line_items,
            "state": "disable"
        }
    }
    return shopify_request("POST", f"orders/{order_id}/refunds.json", refund_payload)

def delete_all():
    limit = 250
    saved_data = load_data("shopify_data_save_new.json")
    
    if not saved_data:
        logging.info("No saved data found. Nothing to delete.")
        return
    
    while True:
        orders = shopify_request("GET", f"orders.json?limit={limit}")
        if not orders or "orders" not in orders or len(orders["orders"]) == 0:
            break
        
        for order in orders["orders"]:
            order_id = order.get("id")
            if order_id:
                logging.info(f"Refunding and canceling order {order_id}...")
                refund_response = refund_order(order_id)
                if refund_response:
                    shopify_request("POST", f"orders/{order_id}/cancel.json")
                    shopify_request("DELETE", f"orders/{order_id}.json")
                    logging.info(f"Order {order_id} deleted successfully.")
                else:
                    logging.warning(f"Failed to refund order {order_id}. Skipping deletion.")
    
    while True:
        products = shopify_request("GET", f"products.json?limit={limit}")
        if not products or "products" not in products or len(products["products"]) == 0:
            break
        
        for product in products["products"]:
            product_id = product.get("id")
            if product_id:
                shopify_request("DELETE", f"products/{product_id}.json")
                logging.info(f"Deleted product {product_id}.")
    
    while True:
        collections = shopify_request("GET", f"custom_collections.json?limit={limit}")
        if not collections or "custom_collections" not in collections or len(collections["custom_collections"]) == 0:
            break
        
        for collection in collections["custom_collections"]:
            collection_id = collection.get("id")
            if collection_id:
                shopify_request("DELETE", f"custom_collections/{collection_id}.json")
                logging.info(f"Deleted custom collection {collection_id}.")
    
    while True:
        collections = shopify_request("GET", f"smart_collections.json?limit={limit}")
        if not collections or "smart_collections" not in collections or len(collections["smart_collections"]) == 0:
            break
        
        for collection in collections["smart_collections"]:
            collection_id = collection.get("id")
            if collection_id:
                shopify_request("DELETE", f"smart_collections/{collection_id}.json")
                logging.info(f"Deleted smart collection {collection_id}.")
    
    while True:
        customers = shopify_request("GET", f"customers.json?limit={limit}")
        if not customers or "customers" not in customers or len(customers["customers"]) == 0:
            break
        
        for customer in customers["customers"]:
            customer_id = customer.get("id")
            if customer_id:
                shopify_request("DELETE", f"customers/{customer_id}.json")
                logging.info(f"Deleted customer {customer_id}.")
    
    logging.info("All records deleted successfully.")
    save_data({})


   
   
if __name__ == "__main__":
    data = {}
    while True:
        print("\nShopify API Operations:")
        print("1. Create Data")
        print("2. Update All Products")
        print("3. Delete All Data")
        print("4. Exit")

        choice = input("Select an option: ")

        if choice == "1":
            data = {}
            data["smart_collections"] = create_resources("smart_collection", "smart_collections")
            data["custom_collections"] = create_resources("custom_collection", "custom_collections")
            data["products"] = create_resources("product", "products")
            data["customers"] = create_resources("customer", "customers")
            data["orders"] = create_orders(data["customers"], data["products"])
            save_data(data)
            logging.info("Batch creation completed!")
        
        elif choice == "2":
            update_product(data["product"]["product"]["id"], "update_product")
            update_product(data["product_with_options"]["product"]["id"], "update_product_with_options")
            product_variant_id = data["product_with_options"]["product"]["variants"][0]["id"]
            update_product_variant_data(data["product_with_options"]["product"]["id"], product_variant_id)
            save_data(data)
        
        elif choice == "3":
            print("Deleting All Data...")
            delete_all()
        
        elif choice == "4":
            break
        else:
            print("Invalid choice, please try again.")