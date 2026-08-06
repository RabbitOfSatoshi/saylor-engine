# ⚡ saylor-engine

> **Interactive MicroStrategy ($MSTR) Satoshi Multiplier & Corporate Substance Dashboard**

[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=flat&logo=Streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An interactive financial analytics dashboard built with **Streamlit** and **Plotly** to evaluate the internal Bitcoin substance, share dilution dynamics (*effective diluted shares*), and leverage effect of MicroStrategy ($MSTR) stock compared to a spot Bitcoin HODL benchmark.

---

## 📊 Overview & Core Features

The **Saylor Engine** precisely evaluates how much physical Bitcoin backing and liquidity reserve a shareholder controls per share and tracks how this corporate substance has developed over time.

### Key Features:
* **JSON Treasury Parser:** Automatically parses local `mstr_treasury_history.json` data sourced from [Saylor Tracker](https://saylortracker.com/) for daily resolution of physical BTC purchases and `effective_diluted_shares`.
* **Dual-Layer Corporate Substance:** Combines physically held BTC with SEC-verified corporate cash reserves (Form 8-K / 10-Q / 10-K) converted into Satoshis.
* **Historical Timeline Chart:** Dynamic resolution of *Free Market Value*, *Spot HODL Benchmark*, *BTC/Share*, and *Total Substance/Share* back to August 2020.
* **Multi-Currency Support (USD / EUR):** Automatic currency conversions via Yahoo Finance API.
* **NAV Premium Simulator:** Live modeling of dynamic changes in market sentiment (-20% to +50% NAV premium/discount).

---

## 🧮 Mathematical Engine & Formulas

All internal metrics convert positions into **Satoshis (1 BTC = 100,000,000 Sats)**:

| Step | Metric | Formula |
| :--- | :--- | :--- |
| **1. Benchmark** | **Spot HODL Sats** | `(Invest_Fiat / BTC_Price_Past) × 100,000,000` |
| **2. Market Value** | **Free Market Value** | `(Shares × MSTR_Price_Simulated / BTC_Price_Curr) × 100,000,000` |
| **3. Core Asset** | **BTC / Share (Sats)** | `(MSTR_BTC_Total / Effective_Diluted_Shares) × 100,000,000` |
| **4. Dry Powder** | **Cash / Share (Sats)** | `(SEC_Cash_USD / Effective_Diluted_Shares / BTC_Price_USD) × 100,000,000` |
| **5. Total** | **Total Substance / Share** | `BTC_per_Share_Sats + Cash_per_Share_Sats` |

---

## 📚 Primary Data Sources

1. **JSON Treasury Tracker (`mstr_treasury_history.json`):**
   * Daily resolution of physical BTC purchases, treasury holdings, and `effective_diluted_shares` sourced from [Saylor Tracker](https://saylortracker.com/).
2. **SEC Filings (MicroStrategy Inc. - CIK 0001050446):**
   * Form 8-K, 10-Q & 10-K for historical and current USD cash reserves.
3. **Yahoo Finance API (`yfinance`):**
   * Live & historical market prices for `MSTR` (split-adjusted), `BTC-USD`, and `EURUSD=X`.

---

## 💻 Tech Stack

* **Frontend Framework:** [Streamlit](https://streamlit.io)
* **Visualizations:** [Plotly Express / Graph Objects](https://plotly.com/python/)
* **Data Processing:** [Pandas](https://pandas.pydata.org/)
* **Financial Data API:** [yfinance](https://pypi.org/project/yfinance/)

---
