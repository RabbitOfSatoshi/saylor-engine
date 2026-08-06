# ⚡ saylor-engine

> **Interactive MicroStrategy ($MSTR) Satoshi Multiplier & Corporate Substance Dashboard**

[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=flat&logo=Streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An interactive financial analytics dashboard built with **Streamlit** and **Plotly** to measure the internal Bitcoin substance and leverage effect of MicroStrategy ($MSTR) stock against a spot Bitcoin HODL benchmark.

---

## 📊 Overview & Core Value

The **Saylor Engine** evaluates how much internal corporate Bitcoin backing and liquidity reserve a shareholder controls compared to directly purchasing spot Bitcoin.

Key analytical metrics:
* **Satoshi Multiplier:** Quantifies corporate BTC backing per share relative to spot markets.
* **Corporate Cash-to-Sats:** Converts corporate USD cash reserves into effective Satoshi exposure.
* **NAV Premium Simulator:** Models dynamic changes in market sentiment (-20% to +50% NAV premium/discount).

---

## 🧮 Mathematical Engine

All core metrics convert positions into **Satoshis (1 BTC = 100,000,000 Sats)**:

| Step | Metric | Formula |
| :--- | :--- | :--- |
| **1. Benchmark** | **Spot HODL Sats** | `(Invest_EUR / BTC_Price_Past) × 100,000,000` |
| **2. Liquidation** | **Market Sats** | `(Market_Value_EUR / BTC_Price_Curr_EUR) × 100,000,000` |
| **3. Core Asset** | **Internal BTC Sats** | `Shares × (MSTR_BTC / Total_Shares) × 100,000,000` |
| **4. Dry Powder** | **Internal Cash Sats** | `(User_Cash_USD / BTC_Price_Curr_USD) × 100,000,000` |
| **5. Total** | **Corporate Substance** | `Internal_BTC_Sats + Internal_Cash_Sats` |

---

## 💻 Tech Stack

* **Frontend Framework:** [Streamlit](https://streamlit.io)
* **Visualizations:** [Plotly Express / Graph Objects](https://plotly.com/python/)
* **Financial Data API:** [yfinance](https://pypi.org/project/yfinance/) (Yahoo Finance)

---

## 🚀 Quick Start (Local Setup)

### 1. Clone the repository
```bash
git clone [https://github.com/YOUR-USERNAME/saylor-engine.git](https://github.com/YOUR-USERNAME/saylor-engine.git)
cd saylor-engine
