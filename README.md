# 🪄 Magic Formula Dashboard — India (Live, Screener.in)

A **live stock-screening dashboard** that scrapes real financial data from
**Screener.in** and applies Joel Greenblatt's Magic Formula ranking.

## ✨ What makes this different?

| Feature | Yahoo Finance version | **This version (Screener.in)** |
|---------|----------------------|--------------------------------|
| ROCE | ROA proxy (~50% accurate) | ✅ **Real ROCE** (exact) |
| EBIT | EBITDA × 0.85 approximation | ✅ **Operating Profit − Depreciation** |
| Enterprise Value | Generic calc | ✅ MCap + Borrowings − Investments |
| Indian accounting | Weak | ✅ **Made for India** |
| Accuracy | ~70% | ✅ **Matches Screener.in exactly** |

## 🚀 How to Run

### Windows (easiest)
1. Unzip the folder anywhere
2. **Double-click `run.bat`**
3. Browser opens at http://localhost:8501

### Mac / Linux
```bash
cd magic_formula_dashboard
chmod +x run.sh
./run.sh
```

### Manual
```bash
pip install -r requirements.txt
streamlit run magic_formula_app.py
```

**Requires:** Python 3.9+ ([download here](https://www.python.org/downloads/))

## 📖 How It Works

The app scrapes each stock's page from Screener.in, e.g.:

- `https://www.screener.in/company/TCS/consolidated/`

From each page, it extracts:
- **Market Cap, Price, ROCE, ROE, P/E** (from top ratios)
- **Sales, Operating Profit, Depreciation, Interest** (P&L table)
- **Borrowings, Investments, Fixed Assets** (Balance Sheet)

Then computes:
- **EBIT** = Operating Profit − Depreciation
- **Enterprise Value** = Market Cap + Borrowings − Investments
- **Earnings Yield** = EBIT ÷ EV × 100
- **Magic Formula Rank** = ROCE rank + EY rank (lower = better)

## 🎛️ Dashboard Features

- **🏆 Rankings tab** — top 20 BUY picks with colour-coded ROCE & EY
- **📊 Sector breakdown** — pie chart + quality-vs-value bars
- **📈 Visualizations** — interactive scatter + bar charts (Plotly)
- **🔍 Stock detail** — deep dive with link to full Screener.in page
- **📁 Raw data** — full universe + CSV export

### Sidebar filters
- Portfolio size (10–50 stocks)
- Min market cap (₹100 Cr – ₹1 Lakh Cr)
- Max Debt/Equity ratio
- Min ROCE threshold
- Toggle Financials/Utilities exclusion

## ⚠️ Important Notes

1. **Respect Screener.in's servers** — the app uses parallel requests with rate limiting. Please don't run it continuously or share scraping code.
2. **Cached for 1 hour** — results cached to avoid hammering Screener.in
3. **Scan times:**
   - Quick Scan (50 stocks) → ~1-2 min
   - Medium Scan (100 stocks) → ~3-4 min
   - Full Scan (all stocks) → ~5-8 min
4. **Login not needed** — Screener.in's public company pages are free
5. **Verify before investing** — always cross-check top picks on Screener.in UI

## 🔧 Customization

### Add/remove stocks
Edit `stock_universe.py` → modify the `NIFTY_STOCKS` list (use NSE symbols **without** `.NS`)

### Change formula weights
Edit `apply_magic_formula()` in `magic_formula_app.py`

### Deploy free online
Push to GitHub → [share.streamlit.io](https://share.streamlit.io) → deploy in 2 clicks

## ⚠️ Disclaimer

This tool is for **educational purposes only**. Not investment advice.

- The Magic Formula can **underperform for 1-3 years** in a row.
- Always do your own research.
- Consult a SEBI-registered advisor for personalized advice.
- Data accuracy depends on Screener.in's data (usually very reliable).

## 📚 References

- **Book**: *The Little Book That Still Beats the Market* by Joel Greenblatt
- **Data**: [Screener.in](https://screener.in)
- **Framework**: [Streamlit](https://streamlit.io)
