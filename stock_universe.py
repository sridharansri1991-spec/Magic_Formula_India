"""
NSE stock universe for Screener.in scraping.
Note: Screener.in uses NSE symbol WITHOUT .NS suffix.
"""

NIFTY_STOCKS = [
    # ── IT ──
    "TCS","INFY","WIPRO","HCLTECH","LTIM","TECHM","MPHASIS","PERSISTENT",
    "COFORGE","OFSS","LTTS","KPITTECH","TATAELXSI","CYIENT","BSOFT","ZENSARTECH",
    
    # ── Banks / NBFC / Insurance (auto-excluded by formula)
    "HDFCBANK","ICICIBANK","KOTAKBANK","AXISBANK","SBIN","BAJFINANCE","BAJAJFINSV",
    "HDFCLIFE","SBILIFE","ICICIPRULI","INDUSINDBK","FEDERALBNK","IDFCFIRSTB",
    "AUBANK","CHOLAFIN","MUTHOOTFIN","LICHSGFIN","CANBK","PNB","BANKBARODA",
    
    # ── FMCG / Consumer
    "HINDUNILVR","ITC","NESTLEIND","BRITANNIA","MARICO","COLPAL","DABUR",
    "GODREJCP","EMAMILTD","TATACONSUM","VBL","UBL","RADICO","JUBLFOOD","DEVYANI",
    
    # ── Auto
    "MARUTI","TATAMOTORS","M&M","BAJAJ-AUTO","HEROMOTOCO","EICHERMOT",
    "ASHOKLEY","TVSMOTOR","BOSCHLTD","MOTHERSON","BALKRISIND","APOLLOTYRE","MRF","EXIDEIND",
    
    # ── Pharma / Healthcare
    "SUNPHARMA","DRREDDY","CIPLA","DIVISLAB","APOLLOHOSP","ZYDUSLIFE",
    "TORNTPHARM","AUROPHARMA","LUPIN","BIOCON","ALKEM","ABBOTINDIA","GLAND",
    "LAURUSLABS","MANKIND","MAXHEALTH","FORTIS","GLENMARK",
    
    # ── Metals & Mining
    "TATASTEEL","JSWSTEEL","HINDALCO","VEDL","COALINDIA","NMDC","SAIL",
    "JINDALSTEL","HINDCOPPER","NATIONALUM","APLAPOLLO",
    
    # ── Oil & Gas
    "RELIANCE","ONGC","BPCL","IOC","HINDPETRO","GAIL","PETRONET","OIL",
    
    # ── Power / Utilities (auto-excluded)
    "NTPC","POWERGRID","TATAPOWER","ADANIPOWER","JSWENERGY","NHPC","SJVN",
    
    # ── Cement
    "ULTRACEMCO","SHREECEM","GRASIM","AMBUJACEM","ACC","DALBHARAT","JKCEMENT","RAMCOCEM",
    
    # ── Telecom
    "BHARTIARTL","IDEA","TATACOMM",
    
    # ── Consumer Durables / Paints
    "TITAN","ASIANPAINT","BERGEPAINT","PIDILITIND","HAVELLS","VOLTAS",
    "DIXON","CROMPTON","WHIRLPOOL","KAJARIACER","POLYCAB","KEI",
    
    # ── Retail
    "TRENT","DMART","ABFRL","VMART","RELAXO","BATAINDIA","PAGEIND","NYKAA",
    
    # ── Industrial / Cap Goods
    "LT","SIEMENS","ABB","BHEL","BEL","CUMMINSIND","THERMAX","HAL","BDL",
    "MAZDOCK","COCHINSHIP","GRSE","ASTRAL","SUPREMEIND",
    
    # ── Chemicals / Fertilisers
    "UPL","PIIND","SRF","AARTIIND","DEEPAKNTR","COROMANDEL","CHAMBLFERT",
    "GNFC","NAVINFLUOR","ATUL","FINEORG","CLEAN","TATACHEM","BALRAMCHIN",
    
    # ── Infra / Realty
    "DLF","LODHA","GODREJPROP","OBEROIRLTY","PRESTIGE","BRIGADE","PHOENIXLTD",
    
    # ── Logistics / Aviation
    "ADANIPORTS","CONCOR","GMRINFRA","INTERGLOBE","IRCTC","IRFC","RVNL",
    
    # ── Adani Group / Others
    "ADANIENT","ADANIGREEN","ADANIENSOL","ZOMATO","PAYTM","POLICYBZR",
]

# De-duplicate and sort
NIFTY_STOCKS = sorted(set(NIFTY_STOCKS))

# Sectors to exclude by keyword (Greenblatt rule)
EXCLUDE_KEYWORDS = [
    "BANK","BNK","FINANCE","FINSV","LIFE","PRULI","HSGFIN","MUTHOOT","CHOLAFIN",
    "POWER","NTPC","POWERGRID","NHPC","SJVN","JSWENERGY","TATAPOWER","ADANIPOWER",
]

def is_excluded(symbol, sector_hint=""):
    """Check if a stock should be excluded (financials/utilities)"""
    sym_up = symbol.upper()
    for kw in EXCLUDE_KEYWORDS:
        if kw in sym_up:
            return True
    if sector_hint and any(s in sector_hint.lower() for s in ["bank","insur","finan","utilit","power"]):
        return True
    return False
