"""
generate_data.py
Synthetic beauty products sales dataset generator.

Can be run standalone to (re)create data/beauty_products.csv:
    python3 generate_data.py

Or imported by app.py to generate the dataframe in-memory (no subprocess,
no file-write dependency) — important for read-only deployment filesystems
like Streamlit Community Cloud.
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def generate_dataset(n: int = 600, seed: int = 42) -> pd.DataFrame:
    """Return a freshly generated synthetic beauty-products dataframe."""
    rng = np.random.default_rng(seed)

    brands = ["GlowLab", "Rougeon", "SunKissed", "LashPro", "PureEarth",
              "BloomBeauty", "SilkStrand", "VelvetSkin", "NuraBeauty", "AuraCare"]

    categories = {
        "Skincare": ["Facial Serum", "Moisturizer", "Face Mask", "Toner",
                     "Sunscreen Lotion", "Cleanser", "Eye Cream"],
        "Makeup": ["Liquid Lipstick", "Mascara", "Foundation", "Highlighter Palette",
                   "Eyeshadow Palette", "Concealer", "Blush"],
        "Haircare": ["Hair Serum", "Shampoo", "Conditioner", "Hair Mask", "Hair Oil"],
        "Fragrance": ["Eau de Parfum", "Body Mist", "Cologne"],
        "Bath & Body": ["Body Lotion", "Body Scrub", "Shower Gel", "Hand Cream"],
    }
    category_names = list(categories.keys())
    category_p = [0.35, 0.30, 0.15, 0.10, 0.10]

    skin_types = ["Dry", "Oily", "Combination", "Sensitive", "All"]
    regions = ["North America", "Europe", "Asia Pacific", "Middle East", "Latin America"]
    channels = ["Online", "In-Store", "Marketplace"]

    start_date = datetime(2024, 1, 1)
    date_range_days = 545  # ~18 months

    rows = []
    for i in range(1, n + 1):
        category = rng.choice(category_names, p=category_p)
        product_type = rng.choice(categories[category])
        brand = rng.choice(brands)
        product_name = f"{brand} {product_type}"

        base_price = {
            "Skincare": 28, "Makeup": 20, "Haircare": 18, "Fragrance": 55, "Bath & Body": 15
        }[category]
        price = round(max(4.99, rng.normal(base_price, base_price * 0.35)), 2)

        rating = round(float(np.clip(rng.normal(4.3, 0.4), 1.0, 5.0)), 1)
        review_count = int(rng.exponential(scale=500))
        skin_type = rng.choice(skin_types)
        stock_quantity = int(rng.integers(0, 500))
        units_sold = int(max(0, rng.exponential(scale=120) - (price / 10)))
        revenue = round(units_sold * price, 2)
        region = rng.choice(regions)
        channel = rng.choice(channels, p=[0.55, 0.30, 0.15])
        order_date = start_date + timedelta(days=int(rng.integers(0, date_range_days)))
        is_cruelty_free = rng.choice(["Yes", "No"], p=[0.65, 0.35])
        discount_pct = int(rng.choice(
            [0, 0, 0, 5, 10, 15, 20, 25, 30],
            p=[0.35, 0.1, 0.1, 0.1, 0.1, 0.1, 0.05, 0.05, 0.05]
        ))

        rows.append({
            "ProductID": f"BP{i:04d}",
            "ProductName": product_name,
            "Brand": brand,
            "Category": category,
            "SubCategory": product_type,
            "Price": price,
            "DiscountPct": discount_pct,
            "Rating": rating,
            "ReviewCount": review_count,
            "SkinType": skin_type,
            "StockQuantity": stock_quantity,
            "UnitsSold": units_sold,
            "Revenue": revenue,
            "Region": region,
            "SalesChannel": channel,
            "CrueltyFree": is_cruelty_free,
            "OrderDate": order_date.strftime("%Y-%m-%d"),
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = generate_dataset()
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "beauty_products.csv")
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df)} rows -> {out_path}")
    print(df.head())
