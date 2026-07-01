# 💄 Beauty Products Sales Dashboard

An interactive Streamlit dashboard built on a synthetic beauty-products sales dataset.

## Files

| File | Purpose |
|---|---|
| `app.py` | The Streamlit dashboard application |
| `generate_data.py` | Generates the synthetic dataset (`data/beauty_products.csv`) |
| `data/beauty_products.csv` | 600-row synthetic dataset (pre-generated, regenerate any time) |
| `requirements.txt` | Python dependencies |

## Dataset columns

`ProductID, ProductName, Brand, Category, SubCategory, Price, DiscountPct, Rating, ReviewCount, SkinType, StockQuantity, UnitsSold, Revenue, Region, SalesChannel, CrueltyFree, OrderDate`

Categories: Skincare, Makeup, Haircare, Fragrance, Bath & Body — spread across 10 brands, 5 regions, and 3 sales channels, with order dates spanning ~18 months.

## Setup

```bash
pip install -r requirements.txt
```

(Optional) regenerate the dataset with different random data:

```bash
python3 generate_data.py
```

## Run the dashboard

```bash
streamlit run app.py
```

Then open the URL Streamlit prints (usually `http://localhost:8501`).

## What's in the dashboard

- **Sidebar filters**: date range, category, brand, region, sales channel, skin type, price range, cruelty-free toggle, plus a button to regenerate fresh synthetic data on the fly.
- **KPI row**: total revenue, units sold, average rating, product count, average price.
- **Charts**: revenue by category, weekly revenue trend, top brands by units sold, sales channel split, price vs. rating scatter (sized by review count), revenue by region, skin-type mix, and a low-stock alert table.
- **Data table**: filtered results with a CSV download button.

## Notes

- All data is synthetically generated with NumPy (seeded for reproducibility) — it does not represent real products or sales.
- If `data/beauty_products.csv` is missing when the app starts, it's generated automatically.
