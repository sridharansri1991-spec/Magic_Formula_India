"""
🪄 MAGIC FORMULA DASHBOARD — INDIA (Live, via Screener.in)
============================================================
Live stock screening dashboard using REAL Screener.in data — exact
ROCE and EBIT values, not approximations.

Run:
    pip install -r requirements.txt
    streamlit run magic_formula_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

from stock_universe import NIFTY_STOCKS, is_excluded
from screener_scraper import scrape_bulk, scrape_one

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Magic Formula — India Live",
    page_icon="🪄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# STYLING
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main { padding-top: 0.5rem; }
    .stMetric { background:#F8F9FA; padding:12px; border-radius:8px;
                border-left:4px solid #1F3864; }
    .stMetric label { font-size:12px !important; color:#666 !important; }
    .stMetric [data-testid="stMetricValue"] { font-size:22px !important; color:#1F3864 !important; }
    div[data-testid="stSidebar"] { background:#F0F3F7; }
    h1,h2,h3 { color:#1F3864; }
    .big-title { font-size:38px; font-weight:bold;
                 background:linear-gradient(90deg,#1F3864,#2E86AB);
                 -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                 margin-bottom:4px; }
    .subtitle { color:#666; font-size:14px; margin-bottom:18px; }
    .source-badge { background:#E8F5E9; color:#1B5E20; padding:4px 10px;
                    border-radius:12px; font-size:11px; font-weight:bold;
                    display:inline-block; margin-right:6px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
col_title, col_status = st.columns([3, 1])
with col_title:
    st.markdown('<div class="big-title">🪄 Magic Formula Dashboard — India</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">'
        '<span class="source-badge">📡 Live from Screener.in</span>'
        '<span class="source-badge">🇮🇳 NSE Stocks</span>'
        '<span class="source-badge">🪄 Joel Greenblatt Method</span>'
        '</div>', unsafe_allow_html=True)
with col_status:
    st.markdown(
        f'<div style="text-align:right; padding-top:20px;">'
        f'<span style="background:#D5F5E3; color:#1E8449; padding:6px 12px; '
        f'border-radius:6px; font-weight:bold; font-size:12px;">● LIVE</span>'
        f'<br><span style="font-size:11px;color:#666; padding-top:4px; display:inline-block;">'
        f'{datetime.now().strftime("%d %b %Y, %I:%M %p")}</span></div>',
        unsafe_allow_html=True)
st.divider()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
st.sidebar.markdown("## ⚙️ Settings")

universe_choice = st.sidebar.selectbox(
    "📊 Stock Universe",
    ["Quick Scan (Top 50)", "Medium Scan (Top 100)", "Full Scan (All Stocks)", "Custom List"],
    index=0,
    help="More stocks = slower scan. Full scan takes ~5-8 min."
)

portfolio_size = st.sidebar.slider("🎯 Portfolio Size (Top N)", 10, 50, 20, step=5)
min_mcap       = st.sidebar.number_input("💰 Min Market Cap (₹ Cr)", 100, 100000, 1000, step=500)
max_de         = st.sidebar.slider("⚠️ Max Debt/Equity (Borrowings ÷ Reserves)",
                                    0.0, 5.0, 2.0, step=0.1)
min_roce       = st.sidebar.slider("📈 Min ROCE %", 0, 50, 10, step=5)

exclude_fin    = st.sidebar.checkbox("🚫 Exclude Financials (Banks/NBFC/Insurance)", value=True)
exclude_util   = st.sidebar.checkbox("🚫 Exclude Utilities (Power)", value=True)

st.sidebar.divider()
st.sidebar.markdown("### 🔄 Refresh")
if st.sidebar.button("🔄 Re-scan Screener.in", use_container_width=True, type="primary"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.divider()
with st.sidebar.expander("ℹ️ About Magic Formula"):
    st.markdown("""
**Joel Greenblatt's Magic Formula** ranks stocks by:

- **ROCE** = Return on Capital Employed → **Quality**
  (Pulled LIVE from Screener.in — exact Screener number)
  
- **Earnings Yield** = EBIT ÷ Enterprise Value → **Value**
  (EBIT = Operating Profit − Depreciation, EV = MCap + Debt − Investments)

Lower combined rank = Better stock. Buy top 20-30, hold 1 year.

**Data source**: Screener.in (scraped in real-time).
""")

# ─────────────────────────────────────────────
# DATA FETCH
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_data(tickers):
    """Scrape Screener.in for all tickers."""
    results = []

    progress = st.progress(0.0, text="Starting scan...")
    status   = st.empty()

    def callback(done, total, sym):
        pct = done / total
        progress.progress(pct, text=f"📡 Scraping {sym}... ({done}/{total})")

    results = scrape_bulk(list(tickers), max_workers=6, progress_callback=callback)

    progress.empty()
    status.empty()
    return pd.DataFrame(results)


def apply_magic_formula(df, min_mcap, max_de, min_roce, exclude_fin, exclude_util):
    """Apply Greenblatt's ranking."""
    df = df.copy()

    # Keep only rows with key data
    df = df[df["mcap_cr"].notna() & df["roce_pct"].notna() &
            df["earnings_yield_pct"].notna()]

    # Filter 1: Market cap
    df = df[df["mcap_cr"] >= min_mcap]

    # Filter 2: Positive ROCE and EY
    df = df[(df["roce_pct"] >= min_roce) & (df["earnings_yield_pct"] > 0)]

    # Filter 3: Debt/Equity
    if "de_ratio" in df.columns:
        df = df[(df["de_ratio"].isna()) | (df["de_ratio"] <= max_de)]

    # Filter 4: Exclude sectors by symbol keywords
    if exclude_fin or exclude_util:
        def keep(row):
            sym = str(row["symbol"]).upper()
            if exclude_fin and any(kw in sym for kw in
                ["BANK","BNK","FINANCE","FINSV","LIFE","PRULI","HSGFIN","MUTHOOT","CHOLAFIN"]):
                return False
            if exclude_util and any(kw in sym for kw in
                ["NTPC","POWERGRID","NHPC","SJVN","JSWENERGY","TATAPOWER","ADANIPOWER"]):
                return False
            return True
        df = df[df.apply(keep, axis=1)]

    if len(df) == 0:
        return df

    # ── Ranking
    df["roce_rank"] = df["roce_pct"].rank(ascending=False, method="min").astype(int)
    df["ey_rank"]   = df["earnings_yield_pct"].rank(ascending=False, method="min").astype(int)
    df["mf_score"]  = df["roce_rank"] + df["ey_rank"]
    df["mf_rank"]   = df["mf_score"].rank(ascending=True, method="min").astype(int)

    return df.sort_values("mf_rank").reset_index(drop=True)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if universe_choice == "Quick Scan (Top 50)":
    tickers = NIFTY_STOCKS[:50]
elif universe_choice == "Medium Scan (Top 100)":
    tickers = NIFTY_STOCKS[:100]
elif universe_choice == "Full Scan (All Stocks)":
    tickers = NIFTY_STOCKS
else:
    custom = st.sidebar.text_area("Custom NSE symbols (one per line, no .NS)",
                                   "TCS\nINFY\nWIPRO\nHCLTECH\nLTIM")
    tickers = [t.strip().upper() for t in custom.split("\n") if t.strip()]

with st.spinner(f"📡 Scanning {len(tickers)} stocks from Screener.in..."):
    df_raw = fetch_data(tuple(tickers))

if df_raw.empty:
    st.error("❌ No data fetched. Possible causes:\n"
             "- Screener.in blocked the request (try again in 1 min)\n"
             "- Network issue\n"
             "- All stocks failed to parse")
    st.stop()

df_ranked = apply_magic_formula(df_raw, min_mcap, max_de, min_roce,
                                 exclude_fin, exclude_util)

# ─────────────────────────────────────────────
# TOP METRICS
# ─────────────────────────────────────────────
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("📊 Stocks Scanned", len(df_raw))
m2.metric("✅ Passed Filters", len(df_ranked))
m3.metric("🎯 Top Picks", min(portfolio_size, len(df_ranked)))
if len(df_ranked) > 0:
    m4.metric("📈 Avg ROCE (Top)",
              f"{df_ranked.head(portfolio_size)['roce_pct'].mean():.1f}%")
    m5.metric("💰 Avg EY (Top)",
              f"{df_ranked.head(portfolio_size)['earnings_yield_pct'].mean():.2f}%")

st.divider()

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏆 Magic Formula Rankings",
    "📊 Sector Breakdown",
    "📈 Visualizations",
    "🔍 Stock Detail",
    "📁 Raw Data",
])

# ── TAB 1: RANKINGS ─────────────────────────────────
with tab1:
    st.markdown("### 🏆 Top Magic Formula Picks (LIVE from Screener.in)")
    top = df_ranked.head(max(portfolio_size, 30)).copy()

    if len(top) > 0:
        def action(r):
            if r <= portfolio_size: return "🟢 BUY"
            elif r <= portfolio_size + 10: return "🟡 WATCH"
            else: return "🔴 SKIP"
        top["Action"] = top["mf_rank"].apply(action)

        cols = ["mf_rank","symbol","name","price","mcap_cr","ebit_cr","ev_cr",
                "roce_pct","earnings_yield_pct","roce_rank","ey_rank","mf_score","Action"]
        disp = top[[c for c in cols if c in top.columns]].copy()

        # Rename
        rename = {
            "mf_rank":"MF Rank","symbol":"Symbol","name":"Company",
            "price":"Price (₹)","mcap_cr":"M.Cap (₹Cr)","ebit_cr":"EBIT (₹Cr)",
            "ev_cr":"EV (₹Cr)","roce_pct":"ROCE %","earnings_yield_pct":"EY %",
            "roce_rank":"ROCE Rank","ey_rank":"EY Rank","mf_score":"Score"
        }
        disp = disp.rename(columns=rename)

        fmt_dict = {
            "Price (₹)": "{:,.2f}",
            "M.Cap (₹Cr)": "{:,.0f}",
            "EBIT (₹Cr)": "{:,.0f}",
            "EV (₹Cr)": "{:,.0f}",
            "ROCE %": "{:.2f}",
            "EY %": "{:.2f}",
        }
        fmt_dict = {k:v for k,v in fmt_dict.items() if k in disp.columns}

        styled = (disp.style.format(fmt_dict)
                  .background_gradient(cmap="RdYlGn", subset=[c for c in ["ROCE %","EY %"] if c in disp.columns])
                  .background_gradient(cmap="RdYlGn_r", subset=[c for c in ["Score","MF Rank"] if c in disp.columns]))

        st.dataframe(styled, use_container_width=True, height=650, hide_index=True)

        csv = top.to_csv(index=False).encode()
        st.download_button("📥 Download Top Picks (CSV)", csv,
                           file_name=f"magic_formula_top_{datetime.now():%Y%m%d}.csv",
                           mime="text/csv")
    else:
        st.warning("⚠️ No stocks passed your filters. Try relaxing Min Market Cap / Min ROCE.")

# ── TAB 2: SECTOR BREAKDOWN ────────────────────────
with tab2:
    if len(df_ranked) > 0:
        top = df_ranked.head(portfolio_size)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🏭 Portfolio Distribution (by company count)")
            # Use symbol prefix as crude sector proxy if sector not scraped
            if "sector" in top.columns and top["sector"].notna().any():
                sec = top["sector"].fillna("Others").value_counts().reset_index()
            else:
                sec = pd.DataFrame({"sector": ["All Sectors"], "count": [len(top)]})
            sec.columns = ["Sector","Count"]
            fig = px.pie(sec, values="Count", names="Sector", hole=0.5,
                         color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.markdown("#### 📊 Quality vs Value — Top Picks")
            chart_df = top[["symbol","roce_pct","earnings_yield_pct"]].set_index("symbol")
            st.bar_chart(chart_df, height=400, color=["#1E8449","#1A5276"])

# ── TAB 3: VISUALIZATIONS ───────────────────────────
with tab3:
    if len(df_ranked) > 0:
        top50 = df_ranked.head(min(50, len(df_ranked)))

        st.markdown("#### 🎯 ROCE vs Earnings Yield — Scatter (Bubble = Market Cap)")
        fig = px.scatter(top50, x="earnings_yield_pct", y="roce_pct",
                         size="mcap_cr", color="mf_rank",
                         hover_data=["symbol","name","mf_rank"],
                         color_continuous_scale="RdYlGn_r",
                         labels={"earnings_yield_pct":"Earnings Yield %",
                                 "roce_pct":"ROCE %"},
                         title=f"Top {len(top50)} Magic Formula Candidates")
        fig.add_vline(x=top50["earnings_yield_pct"].median(),
                      line_dash="dash", line_color="gray",
                      annotation_text="Median EY")
        fig.add_hline(y=top50["roce_pct"].median(),
                      line_dash="dash", line_color="gray",
                      annotation_text="Median ROCE")
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### 🏆 Top 20 Ranked — ROCE vs EY Bar Chart")
        bar = df_ranked.head(20)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=bar["symbol"], y=bar["roce_pct"],
                              name="ROCE %", marker_color="#1E8449"))
        fig2.add_trace(go.Bar(x=bar["symbol"], y=bar["earnings_yield_pct"],
                              name="EY %", marker_color="#1A5276"))
        fig2.update_layout(barmode="group", height=450,
                           xaxis_tickangle=-45,
                           title="ROCE vs EY — Top 20 Magic Formula Picks")
        st.plotly_chart(fig2, use_container_width=True)

# ── TAB 4: STOCK DETAIL ─────────────────────────────
with tab4:
    if len(df_ranked) > 0:
        sel = st.selectbox("🔍 Select stock for deep-dive", df_ranked["symbol"].tolist())
        s = df_ranked[df_ranked["symbol"] == sel].iloc[0]

        st.markdown(f"### {s.get('name', sel)} ({sel})")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Price", f"₹{s.get('price', 0):,.2f}")
        c2.metric("Market Cap", f"₹{s.get('mcap_cr', 0):,.0f} Cr")
        c3.metric("MF Rank", f"#{int(s['mf_rank'])}")
        c4.metric("Score", f"{int(s['mf_score'])}")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🪄 Magic Formula Metrics")
            st.markdown(f"""
| Metric | Value |
|---|---|
| **ROCE** | {s.get('roce_pct',0):.2f}% (Rank #{int(s['roce_rank'])}) |
| **Earnings Yield** | {s.get('earnings_yield_pct',0):.2f}% (Rank #{int(s['ey_rank'])}) |
| **EBIT** | ₹{s.get('ebit_cr',0):,.0f} Cr |
| **Enterprise Value** | ₹{s.get('ev_cr',0):,.0f} Cr |
| **Combined Score** | {int(s['mf_score'])} |
""")
        with c2:
            st.markdown("#### 💼 Financials (Screener.in)")
            st.markdown(f"""
| Metric | Value |
|---|---|
| **Sales** | ₹{s.get('sales_cr',0):,.0f} Cr |
| **Operating Profit** | ₹{s.get('op_profit_cr',0):,.0f} Cr |
| **Net Profit** | ₹{s.get('net_profit_cr',0):,.0f} Cr |
| **Borrowings** | ₹{s.get('borrowings_cr',0):,.0f} Cr |
| **Investments** | ₹{s.get('investments_cr',0):,.0f} Cr |
| **P/E** | {s.get('pe',0):.2f} |
| **ROE** | {s.get('roe_pct',0):.2f}% |
| **Div Yield** | {s.get('div_yield',0):.2f}% |
""")
        st.link_button(f"📖 View full {sel} page on Screener.in",
                       f"https://www.screener.in/company/{sel}/",
                       type="secondary")

# ── TAB 5: RAW DATA ─────────────────────────────────
with tab5:
    st.markdown("### 📁 Full Scanned Universe")
    st.dataframe(df_raw, use_container_width=True, height=650)
    csv = df_raw.to_csv(index=False).encode()
    st.download_button("📥 Download Full Dataset (CSV)", csv,
                       file_name=f"screener_universe_{datetime.now():%Y%m%d}.csv",
                       mime="text/csv")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.divider()
col_a, col_b = st.columns([3,1])
with col_a:
    st.caption(
        "⚠️ **Disclaimer**: Educational purposes only. Not investment advice. "
        "Data is scraped from Screener.in in real-time. Please respect Screener.in's ToS. "
        "Always verify by visiting the Screener.in page of each stock before investing.")
with col_b:
    st.caption("Built with ❤️ using Streamlit · Screener.in · Plotly")
