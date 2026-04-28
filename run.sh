#!/bin/bash
echo "============================================"
echo "  Magic Formula Dashboard - India"
echo "  Data Source: Screener.in (LIVE)"
echo "============================================"

if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

echo "[1/2] Installing dependencies..."
python3 -m pip install -q -r requirements.txt

echo "[2/2] Launching dashboard at http://localhost:8501 ..."
python3 -m streamlit run magic_formula_app.py
