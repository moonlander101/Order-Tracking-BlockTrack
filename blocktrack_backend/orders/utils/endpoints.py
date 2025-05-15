import os
import httpx

PRODUCTS_API_URL = f"{os.getenv('WAREHOUSE_SERVICE_URL', 'localhost:8001')}/api/product/products/"

def fetch_products():
    with httpx.Client() as client:
        try:
            response = client.get(PRODUCTS_API_URL)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"Error fetching products: {str(e)}")
