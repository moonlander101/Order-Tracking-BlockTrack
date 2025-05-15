import os
import httpx

WAREHOUSE_SERVICE_URL = f"{os.getenv('WAREHOUSE_SERVICE_URL', 'localhost:8001')}"

def fetch_products():
    with httpx.Client() as client:
        try:
            response = client.get(f"{WAREHOUSE_SERVICE_URL}/api/product/products/")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"Error fetching products: {str(e)}")

def fetch_warehouse_details(warehouse_id):
    url = f"{WAREHOUSE_SERVICE_URL}/api/warehouse/warehouses/"
    with httpx.Client() as client:
        try:
            response = client.get(url)
            response.raise_for_status()
            return [x for x in response.json() if x["id"] == warehouse_id][0]
        except httpx.HTTPError as e:
            raise Exception(f"Error fetching warehouse details: {str(e)}")