import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------------
# DB CONNECTION
# -----------------------------
engine = create_engine(
    "postgresql+psycopg2://postgres:Logesh%401234@localhost:5432/postgres"
)

st.set_page_config(layout="wide")
st.title("📊 Data-Driven Stock Analysis Dashboard")

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    vol = pd.read_sql("SELECT * FROM volatility_summary", engine)
    risk = pd.read_sql("SELECT * FROM risk_return", engine)
    gain = pd.read_sql("SELECT * FROM top_gainers", engine)
    loss = pd.read_sql("SELECT * FROM top_losers", engine)
    cum = pd.read_sql("SELECT * FROM cumulative_return", engine)
    sector = pd.read_sql("SELECT * FROM sector_performance", engine)
    corr = pd.read_sql("SELECT * FROM correlation_matrix", engine)
    return vol, risk, gain, loss, cum, sector, corr

vol_df, risk_df, gain_df, loss_df, cum_df, sector_df, corr_df = load_data()

# -----------------------------
# STANDARDIZE COLUMNS
# -----------------------------
risk_df.columns = risk_df.columns.str.lower()
sector_df.columns = sector_df.columns.str.lower()
corr_df.columns = corr_df.columns.str.lower()

# -----------------------------
# SIDEBAR FILTER
# -----------------------------
st.sidebar.header("Filters")

ticker_list = ["All"] + sorted(vol_df["Ticker"].dropna().unique().tolist())

ticker = st.sidebar.selectbox("Select Ticker", ticker_list)

# -----------------------------
# APPLY FILTER
# -----------------------------
if ticker != "All":
    vol_df = vol_df[vol_df["Ticker"] == ticker]

    if "ticker" in risk_df.columns:
        risk_df = risk_df[risk_df["ticker"] == ticker]

    if "Ticker" in gain_df.columns:
        gain_df = gain_df[gain_df["Ticker"] == ticker]

    if "Ticker" in loss_df.columns:
        loss_df = loss_df[loss_df["Ticker"] == ticker]

    if "Ticker" in cum_df.columns:
        cum_df = cum_df[cum_df["Ticker"] == ticker]

# -----------------------------
# ROW 1: GAINERS / LOSERS
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top Gainers")
    if "monthly_return" in gain_df.columns and not gain_df.empty:
        st.bar_chart(gain_df.set_index("Ticker")["monthly_return"])
    else:
        st.info("No valid gainers data")

with col2:
    st.subheader("Top Losers")
    if "monthly_return" in loss_df.columns and not loss_df.empty:
        st.bar_chart(loss_df.set_index("Ticker")["monthly_return"])
    else:
        st.info("No valid losers data")

# -----------------------------
# ROW 2: RISK vs RETURN
# -----------------------------
st.subheader("Risk vs Return")

if {"risk", "return"}.issubset(risk_df.columns):
    st.scatter_chart(risk_df, x="risk", y="return")
else:
    st.warning("Risk/Return columns missing")
    st.dataframe(risk_df)

# -----------------------------
# ROW 3: CUMULATIVE RETURN
# -----------------------------
st.subheader("Cumulative Return")

if "date" in cum_df.columns:
    cum_df["date"] = pd.to_datetime(cum_df["date"])

if {"date", "cumulative_return"}.issubset(cum_df.columns):
    st.line_chart(cum_df, x="date", y="cumulative_return")
else:
    st.warning("Cumulative return data issue")
    st.dataframe(cum_df)

# -----------------------------
# ROW 4: VOLATILITY + SECTOR
# -----------------------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("Volatility")
    if "Annual_Volatility_%" in vol_df.columns and not vol_df.empty:
        st.bar_chart(vol_df.set_index("Ticker")["Annual_Volatility_%"])
    else:
        st.info("No volatility data")

with col4:
    st.subheader("Sector Performance")

    sector_col = None
    value_col = None

    # detect sector column
    for col in sector_df.columns:
        if col in ["sector", "industry"]:
            sector_col = col

    # detect return column
    for col in sector_df.columns:
        if "return" in col:
            value_col = col

    if sector_col and value_col:
        st.bar_chart(sector_df.set_index(sector_col)[value_col])
    else:
        st.warning("Sector data not available")
        st.dataframe(sector_df)

# -----------------------------
# ROW 5: CORRELATION HEATMAP
# -----------------------------
st.subheader("Correlation Heatmap")

# Convert to matrix if needed
if {"stock_1", "stock_2", "correlation"}.issubset(corr_df.columns):
    corr_df = corr_df.pivot(
        index="stock_1",
        columns="stock_2",
        values="correlation"
    )

# Keep only numeric columns
corr_df = corr_df.select_dtypes(include="number")

if not corr_df.empty:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(corr_df, cmap="coolwarm", ax=ax)
    st.pyplot(fig)
else:
    st.warning("Correlation data not available")

# -----------------------------
# KPI CALCULATIONS
# -----------------------------

# Top Performing Stock (based on return)
if {"ticker", "return"}.issubset(risk_df.columns):
    top_stock = risk_df.loc[risk_df["return"].idxmax()]
    top_stock_name = top_stock["ticker"]
    top_stock_return = top_stock["return"]
else:
    top_stock_name = "N/A"
    top_stock_return = 0

# Average Return
if "return" in risk_df.columns:
    avg_return = risk_df["return"].mean()
else:
    avg_return = 0

# Highest Risk Stock
if {"ticker", "risk"}.issubset(risk_df.columns):
    high_risk = risk_df.loc[risk_df["risk"].idxmax()]
    high_risk_name = high_risk["ticker"]
    high_risk_value = high_risk["risk"]
else:
    high_risk_name = "N/A"
    high_risk_value = 0


# -----------------------------
# KPI DISPLAY
# -----------------------------
st.markdown("## 📊 Key Performance Indicators")
kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    st.metric(
        label="🏆 Top Stock",
        value=top_stock_name,
        delta=f"{top_stock_return:.2%}"
    )

with kpi2:
    st.metric(
        label="📈 Avg Return",
        value=f"{avg_return:.2%}"
    )

with kpi3:
    st.metric(
        label="⚠ Highest Risk",
        value=high_risk_name,
        delta=f"{high_risk_value:.2%}"
    )

