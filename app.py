import streamlit as st
import pandas as pd
import plotly.express as px
import os

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="S&P 500 Stock Dashboard",
    layout="wide"
)

st.title("📊 S&P 500 Stock Dashboard (2014–2017)")

# -----------------------------
# Load CSV File Safely
# -----------------------------
FILE_NAME = "adi123.csv"

if not os.path.exists(FILE_NAME):
    st.error(f"File '{FILE_NAME}' not found. Keep it in the same folder as app.py")
    st.stop()

# 🔴 Handle EMPTY CSV safely
try:
    df = pd.read_csv(FILE_NAME)
except pd.errors.EmptyDataError:
    st.error("CSV file is empty. Please add data and try again.")
    st.stop()

# If file loads but has no columns
if df.empty or len(df.columns) == 0:
    st.error("CSV file has no data or headers.")
    st.stop()

# -----------------------------
# Clean & Prepare Data
# -----------------------------
df.columns = df.columns.str.strip().str.lower()

required_columns = {"symbol", "date", "close", "volume"}

if not required_columns.issubset(df.columns):
    st.error("CSV is missing required columns.")
    st.write("Found columns:", df.columns.tolist())
    st.stop()

# Convert date correctly (DD-MM-YYYY)
df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")

# Remove invalid dates
df = df.dropna(subset=["date"])

# Sort chronologically
df = df.sort_values("date")

st.success("Dataset loaded successfully!")

# -----------------------------
# Top 5 Companies by Volume
# -----------------------------
top5_symbols = (
    df.groupby("symbol")["volume"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .index
    .tolist()
)

df_top5 = df[df["symbol"].isin(top5_symbols)].copy()

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("Controls")

selected_symbol = st.sidebar.selectbox(
    "Select Company",
    top5_symbols
)

# -----------------------------
# 1️⃣ Line Chart
# -----------------------------
st.subheader("1️⃣ Line Chart – Stock Price Trend Over Time")

line_data = df_top5[df_top5["symbol"] == selected_symbol]

line_data_daily = (
    line_data
    .groupby("date", as_index=False)["close"]
    .mean()
)
#px.line('')
fig_line = px.line(
    line_data_daily,
    x="date",
    y="close",
    title=f"Closing Price Trend – {selected_symbol}",
    labels={"date": "Date", "close": "Average Closing Price"}
)

st.plotly_chart(fig_line, use_container_width=True)

# -----------------------------
# 2️⃣ Bar Charts
# -----------------------------
st.subheader("2️⃣ Bar Charts – Trading Volume Analysis")

col1, col2 = st.columns(2)

with col1:
    daily_volume = (
        line_data
        .groupby("date", as_index=False)["volume"]
        .sum()
    )

    fig_bar_day = px.bar(
        daily_volume,
        x="date",
        y="volume",
        title=f"Daily Trading Volume – {selected_symbol}"
    )
    st.plotly_chart(fig_bar_day, use_container_width=True)

with col2:
    avg_volume = (
        df_top5.groupby("symbol")["volume"]
        .mean()
        .reset_index()
    )

    fig_bar_avg = px.bar(
        avg_volume,
        x="symbol",
        y="volume",
        title="Average Trading Volume (Top 5 Companies)"
    )
    st.plotly_chart(fig_bar_avg, use_container_width=True)

# -----------------------------
# Yearly Volume
# -----------------------------
df_top5["year"] = df_top5["date"].dt.year

yearly_volume = (
    df_top5.groupby(["year", "symbol"])["volume"]
    .sum()
    .reset_index()
)

fig_bar_year = px.bar(
    yearly_volume,
    x="year",
    y="volume",
    color="symbol",
    barmode="group",
    title="Yearly Trading Volume (Top 5 Companies)"
)

st.plotly_chart(fig_bar_year, use_container_width=True)

# -----------------------------
# 3️⃣ Histogram
# -----------------------------
st.subheader("3️⃣ Histogram – Distribution of Closing Prices")

fig_hist = px.histogram(
    line_data,
    x="close",
    nbins=50,
    title=f"Closing Price Distribution – {selected_symbol}"
)

st.plotly_chart(fig_hist, use_container_width=True)

# -----------------------------
# 4️⃣ Pie Chart
# -----------------------------
st.subheader("4️⃣ Pie Chart – Volume Contribution")

volume_share = (
    df.groupby("symbol")["volume"]
    .sum()
    .sort_values(ascending=False)
)

top5_volume = volume_share.head(5)
others_volume = volume_share.iloc[5:].sum()

pie_df = pd.DataFrame({
    "symbol": list(top5_volume.index) + ["Others"],
    "volume": list(top5_volume.values) + [others_volume]
})

fig_pie = px.pie(
    pie_df,
    names="symbol",
    values="volume",
    title="Trading Volume Share (Top 5 vs Others)"
)

st.plotly_chart(fig_pie, use_container_width=True)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("S&P 500 Stock Analysis Dashboard using Streamlit")
