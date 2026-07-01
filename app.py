"""
app.py
Streamlit dashboard for the synthetic Beauty Products dataset.

Run with:
    streamlit run app.py
"""

import os
import pandas as pd
import streamlit as st
import plotly.express as px

from generate_data import generate_dataset

# ----------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Beauty Products Sales Dashboard",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(APP_DIR, "data", "beauty_products.csv")


# ----------------------------------------------------------------------
# Data loading
# ----------------------------------------------------------------------
# Generates the dataset in-memory (no subprocess call, no dependency on a
# writable filesystem). This is required for platforms like Streamlit
# Community Cloud where the app's source directory is often read-only.
@st.cache_data
def load_data(path: str, seed: int = 42) -> pd.DataFrame:
    if os.path.exists(path):
        try:
            return pd.read_csv(path, parse_dates=["OrderDate"])
        except Exception:
            pass  # fall through to in-memory generation

    df = generate_dataset(seed=seed)
    df["OrderDate"] = pd.to_datetime(df["OrderDate"])

    # Best-effort cache to disk; ignore failures on read-only deployments.
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df.to_csv(path, index=False)
    except OSError:
        pass

    return df


if "data_seed" not in st.session_state:
    st.session_state.data_seed = 42

df = load_data(DATA_PATH, seed=st.session_state.data_seed)

# ----------------------------------------------------------------------
# Sidebar filters
# ----------------------------------------------------------------------
st.sidebar.title("💄 Filters")

min_date, max_date = df["OrderDate"].min(), df["OrderDate"].max()
date_range = st.sidebar.date_input(
    "Order date range",
    value=(min_date.date(), max_date.date()),
    min_value=min_date.date(),
    max_value=max_date.date(),
)

categories = sorted(df["Category"].unique())
sel_categories = st.sidebar.multiselect("Category", categories, default=categories)

brands = sorted(df["Brand"].unique())
sel_brands = st.sidebar.multiselect("Brand", brands, default=brands)

regions = sorted(df["Region"].unique())
sel_regions = st.sidebar.multiselect("Region", regions, default=regions)

channels = sorted(df["SalesChannel"].unique())
sel_channels = st.sidebar.multiselect("Sales Channel", channels, default=channels)

skin_types = sorted(df["SkinType"].unique())
sel_skin = st.sidebar.multiselect("Skin Type", skin_types, default=skin_types)

price_min, price_max = float(df["Price"].min()), float(df["Price"].max())
price_range = st.sidebar.slider(
    "Price range ($)", min_value=round(price_min, 2), max_value=round(price_max, 2),
    value=(round(price_min, 2), round(price_max, 2))
)

cruelty_free_only = st.sidebar.checkbox("Cruelty-free only", value=False)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Regenerate synthetic data"):
    import random
    st.session_state.data_seed = random.randint(0, 1_000_000)
    st.cache_data.clear()
    st.rerun()

# ----------------------------------------------------------------------
# Apply filters
# ----------------------------------------------------------------------
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_d, end_d = date_range
else:
    start_d, end_d = min_date.date(), max_date.date()

mask = (
    (df["OrderDate"].dt.date >= start_d)
    & (df["OrderDate"].dt.date <= end_d)
    & (df["Category"].isin(sel_categories))
    & (df["Brand"].isin(sel_brands))
    & (df["Region"].isin(sel_regions))
    & (df["SalesChannel"].isin(sel_channels))
    & (df["SkinType"].isin(sel_skin))
    & (df["Price"].between(price_range[0], price_range[1]))
)
if cruelty_free_only:
    mask &= df["CrueltyFree"] == "Yes"

fdf = df[mask].copy()

# ----------------------------------------------------------------------
# Header + KPIs
# ----------------------------------------------------------------------
st.title("💄 Beauty Products Sales Dashboard")
st.caption("Synthetic dataset · interactive exploration of sales, ratings, and inventory")

if fdf.empty:
    st.warning("No data matches the selected filters. Try widening your selection.")
    st.stop()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Revenue", f"${fdf['Revenue'].sum():,.0f}")
k2.metric("Units Sold", f"{fdf['UnitsSold'].sum():,}")
k3.metric("Avg. Rating", f"{fdf['Rating'].mean():.2f} ⭐")
k4.metric("Products", f"{fdf['ProductID'].nunique():,}")
k5.metric("Avg. Price", f"${fdf['Price'].mean():.2f}")

st.markdown("---")

# ----------------------------------------------------------------------
# Row 1: Revenue by category, Revenue trend
# ----------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.subheader("Revenue by Category")
    rev_by_cat = fdf.groupby("Category", as_index=False)["Revenue"].sum().sort_values("Revenue", ascending=False)
    fig = px.bar(rev_by_cat, x="Category", y="Revenue", color="Category", text_auto=".2s")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Revenue Trend Over Time")
    trend = fdf.set_index("OrderDate").resample("W")["Revenue"].sum().reset_index()
    fig = px.line(trend, x="OrderDate", y="Revenue", markers=True)
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------
# Row 2: Brand performance, Sales channel split
# ----------------------------------------------------------------------
c3, c4 = st.columns(2)

with c3:
    st.subheader("Top Brands by Units Sold")
    top_brands = fdf.groupby("Brand", as_index=False)["UnitsSold"].sum().sort_values("UnitsSold", ascending=False).head(10)
    fig = px.bar(top_brands, x="UnitsSold", y="Brand", orientation="h", color="UnitsSold",
                 color_continuous_scale="Purples")
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with c4:
    st.subheader("Sales Channel Split")
    ch = fdf.groupby("SalesChannel", as_index=False)["Revenue"].sum()
    fig = px.pie(ch, names="SalesChannel", values="Revenue", hole=0.45)
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------
# Row 3: Price vs Rating, Region breakdown
# ----------------------------------------------------------------------
c5, c6 = st.columns(2)

with c5:
    st.subheader("Price vs. Rating")
    fig = px.scatter(
        fdf, x="Price", y="Rating", color="Category", size="ReviewCount",
        hover_data=["ProductName", "Brand"], opacity=0.7
    )
    st.plotly_chart(fig, use_container_width=True)

with c6:
    st.subheader("Revenue by Region")
    reg = fdf.groupby("Region", as_index=False)["Revenue"].sum().sort_values("Revenue", ascending=False)
    fig = px.bar(reg, x="Region", y="Revenue", color="Region", text_auto=".2s")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------
# Row 4: Skin type distribution, Stock levels
# ----------------------------------------------------------------------
c7, c8 = st.columns(2)

with c7:
    st.subheader("Product Mix by Skin Type")
    skin = fdf["SkinType"].value_counts().reset_index()
    skin.columns = ["SkinType", "Count"]
    fig = px.pie(skin, names="SkinType", values="Count", hole=0.45)
    st.plotly_chart(fig, use_container_width=True)

with c8:
    st.subheader("Low Stock Alert (< 50 units)")
    low_stock = fdf[fdf["StockQuantity"] < 50][
        ["ProductID", "ProductName", "Brand", "StockQuantity"]
    ].sort_values("StockQuantity").head(15)
    if low_stock.empty:
        st.info("No products currently below the low-stock threshold.")
    else:
        st.dataframe(low_stock, use_container_width=True, hide_index=True)

st.markdown("---")

# ----------------------------------------------------------------------
# Data table + download
# ----------------------------------------------------------------------
st.subheader("📋 Filtered Data")
st.dataframe(fdf.sort_values("OrderDate", ascending=False), use_container_width=True, hide_index=True)

csv_bytes = fdf.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download filtered data as CSV",
    data=csv_bytes,
    file_name="beauty_products_filtered.csv",
    mime="text/csv",
)

st.caption("Data is synthetically generated for demo purposes and does not represent real sales.")
