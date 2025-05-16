from decimal import Decimal
from collections import defaultdict
from statistics import mean, stdev

def add_price_competitiveness_score(transactions):
    prices_by_product = {}

    for tx in transactions:
        if tx.get("unit_price") is not None:
            prices_by_product.setdefault(tx["product_id"], []).append(tx["unit_price"])

    stats_by_product = {}
    for product_id, prices in prices_by_product.items():
        if len(prices) > 1:
            stats_by_product[product_id] = {
                "mean": mean(prices),
                "stdev": stdev(prices)
            }
        else:
            stats_by_product[product_id] = {
                "mean": prices[0],
                "stdev": 0
            }

    for tx in transactions:
        product_id = tx["product_id"]
        unit_price = tx.get("unit_price")
        if unit_price is not None:
            stats = stats_by_product[product_id]
            if stats["stdev"] > 0:
                z = (stats["mean"] - unit_price) / stats["stdev"]
                score = max(0, min(10, round(5 + z * 2.5, 2)))
            else:
                score = 10.0
        else:
            score = None
        tx["price_competitiveness"] = score

    return transactions
