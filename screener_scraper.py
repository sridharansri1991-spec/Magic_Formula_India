"""
Screener.in scraper for Indian stocks — Magic Formula edition.
Uses the PUBLIC company pages (no login needed).
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 "
                   "Safari/537.36"),
    "Accept-Language": "en-US,en;q=0.9",
}


def _parse_num(text):
    """Extract a number from strings like '₹8,84,514Cr.' or '63.0%' or '1,234'"""
    if not text: return None
    t = str(text).replace(",","").replace("₹","").replace("Cr.","").replace("%","").strip()
    m = re.search(r"-?\d+\.?\d*", t)
    return float(m.group()) if m else None


def scrape_one(symbol, timeout=15, retries=1):
    """Scrape a single stock from Screener.in — returns dict of metrics."""
    urls = [
        f"https://www.screener.in/company/{symbol}/consolidated/",
        f"https://www.screener.in/company/{symbol}/",
    ]

    html = None
    for attempt in range(retries + 1):
        for url in urls:
            try:
                r = requests.get(url, headers=HEADERS, timeout=timeout)
                if r.status_code == 200 and len(r.text) > 5000:
                    html = r.text
                    break
            except Exception:
                continue
        if html: break
        time.sleep(1)

    if not html:
        return {"symbol": symbol, "error": "fetch_failed"}

    soup = BeautifulSoup(html, "html.parser")
    data = {"symbol": symbol}

    # ── Company name + sector
    h1 = soup.find("h1")
    if h1:
        data["name"] = h1.get_text(strip=True)

    # Sector hint from the "About" section or breadcrumb
    about = soup.find("div", class_="company-profile")
    if about:
        peers = about.find_all("a", href=re.compile(r"^/company/compare"))
        if peers:
            data["sector"] = peers[0].get_text(strip=True)

    # ── Top ratios
    ratios_ul = soup.find("ul", id="top-ratios")
    if ratios_ul:
        for li in ratios_ul.find_all("li"):
            name_span = li.find("span", class_="name")
            if not name_span: continue
            key = name_span.get_text(strip=True)
            val_span = li.find("span", class_="nowrap value") or li.find("span", class_="number")
            if not val_span: continue
            val_text = val_span.get_text(strip=True)

            if key == "Market Cap":       data["mcap_cr"] = _parse_num(val_text)
            elif key == "Current Price":  data["price"] = _parse_num(val_text)
            elif key == "Stock P/E":      data["pe"] = _parse_num(val_text)
            elif key == "ROCE":           data["roce_pct"] = _parse_num(val_text)
            elif key == "ROE":            data["roe_pct"] = _parse_num(val_text)
            elif key == "Book Value":     data["book_value"] = _parse_num(val_text)
            elif key == "Dividend Yield": data["div_yield"] = _parse_num(val_text)
            elif key == "Face Value":     data["face_value"] = _parse_num(val_text)
            elif "High / Low" in key:
                hl = re.findall(r"[\d,]+\.?\d*", val_text)
                if len(hl) >= 2:
                    data["high_52w"] = _parse_num(hl[0])
                    data["low_52w"]  = _parse_num(hl[1])

    # ── Profit & Loss → EBIT = Operating Profit − Depreciation
    pl = soup.find("section", id="profit-loss")
    if pl and pl.find("table"):
        table = pl.find("table")
        headers_row = [th.get_text(strip=True) for th in table.find("thead").find_all("th")]
        has_ttm = "TTM" in headers_row[-1] if headers_row else False

        def pl_row(keyword):
            for row in table.find("tbody").find_all("tr"):
                cells = row.find_all("td")
                if cells and keyword in cells[0].get_text(strip=True):
                    vals = [c.get_text(strip=True) for c in cells[1:]]
                    # Prefer TTM, else latest year
                    idx = -1 if has_ttm else -1
                    return _parse_num(vals[idx])
            return None

        op_profit = pl_row("Operating Profit")
        depr      = pl_row("Depreciation")
        interest  = pl_row("Interest")
        sales     = pl_row("Sales")
        net_prof  = pl_row("Net Profit")

        data["sales_cr"]     = sales
        data["op_profit_cr"] = op_profit
        data["depr_cr"]      = depr
        data["interest_cr"]  = interest
        data["net_profit_cr"]= net_prof

        if op_profit is not None and depr is not None:
            data["ebit_cr"] = op_profit - depr

    # ── Balance Sheet → Debt, Cash, Fixed Assets
    bs = soup.find("section", id="balance-sheet")
    if bs and bs.find("table"):
        table = bs.find("table")

        def bs_row(keyword):
            for row in table.find("tbody").find_all("tr"):
                cells = row.find_all("td")
                if cells and keyword in cells[0].get_text(strip=True):
                    vals = [c.get_text(strip=True) for c in cells[1:]]
                    return _parse_num(vals[-1])
            return None

        data["borrowings_cr"]   = bs_row("Borrowings")
        data["investments_cr"]  = bs_row("Investments")
        data["fixed_assets_cr"] = bs_row("Fixed Assets")
        data["reserves_cr"]     = bs_row("Reserves")
        data["total_assets_cr"] = bs_row("Total Assets")
        data["other_assets_cr"] = bs_row("Other Assets")

    # ── Derived metrics (Magic Formula)
    mcap = data.get("mcap_cr")
    ebit = data.get("ebit_cr")
    borr = data.get("borrowings_cr") or 0
    invs = data.get("investments_cr") or 0

    if mcap and ebit is not None:
        # Enterprise Value = MCap + Debt − Cash/Investments (approximation)
        ev = mcap + borr - invs
        data["ev_cr"] = max(ev, mcap * 0.7)  # sanity floor
        if data["ev_cr"] > 0:
            data["earnings_yield_pct"] = ebit / data["ev_cr"] * 100

    # Debt/Equity calculation
    reserves = data.get("reserves_cr") or 0
    if reserves > 0:
        data["de_ratio"] = borr / reserves
    else:
        data["de_ratio"] = None

    return data


def scrape_bulk(symbols, max_workers=5, progress_callback=None):
    """Scrape multiple stocks in parallel."""
    results = []
    done = 0
    total = len(symbols)

    with ThreadPoolExecutor(max_workers=max_workers) as exe:
        futures = {exe.submit(scrape_one, s): s for s in symbols}
        for fut in as_completed(futures):
            sym = futures[fut]
            try:
                result = fut.result()
                if result and "error" not in result:
                    results.append(result)
            except Exception as e:
                pass
            done += 1
            if progress_callback:
                progress_callback(done, total, sym)

    return results
