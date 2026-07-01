"""
generate_data.py
Generates a synthetic beauty products sales dataset for the Streamlit dashboard.
Run this once (or via the dashboard's "Regenerate" button) to (re)create data/beauty_products.csv
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Reproducibility
np.random.seed(42)

N = 600  # number of rows

# ---- Reference lists ----
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

skin_types = ["Dry", "Oily", "Combination", "Sensitive", "All"]
regions = ["North America", "Europe", "Asia Pacific", "Middle East", "Latin America"]
channels = ["Online", "In-Store", "Marketplace"]

# ---- Build rows ----
rows = []
start_date = datetime(2024, 1, 1)
date_range_days = 545  # ~18 months of possible order dates

for i in range(1, N + 1):
    category = np.random.choice(list(categories.keys()), p=[0.35, 0.30, 0.15, 0.10, 0.10])
    product_type = np.random.choice(categories[category])
    brand = np.random.choice(brands)
    product_name = f"{brand} {product_type}"

    base_price = {
        "Skincare": 28, "Makeup": 20, "Haircare": 18, "Fragrance": 55, "Bath & Body": 15
    }[category]
    price = round(max(4.99, np.random.normal(base_price, base_price * 0.35)), 2)

    rating = round(np.clip(np.random.normal(4.3, 0.4), 1.0, 5.0), 1)
    review_count = int(np.random.exponential(scale=500))
    skin_type = np.random.choice(skin_types)
    stock_quantity = int(np.random.randint(0, 500))
    units_sold = int(max(0, np.random.exponential(scale=120) - (price / 10)))
    revenue = round(units_sold * price, 2)
    region = np.random.choice(regions)
    channel = np.random.choice(channels, p=[0.55, 0.30, 0.15])
    order_date = start_date + timedelta(days=int(np.random.randint(0, date_range_days)))
    is_cruelty_free = np.random.choice(["Yes", "No"], p=[0.65, 0.35])
    discount_pct = int(np.random.choice(
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

df = pd.DataFrame(rows)

os.makedirs("data", exist_ok=True)
out_path = "data/beauty_products.csv"
df.to_csv(out_path, index=False)
print(f"Generated {len(df)} rows -> {out_path}")
print(df.head())
