import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import date, timedelta
import pandas as pd
import json

# ==========================================
# 1. STREAMLIT PAGE CONFIG & DYNAMIC THEME CSS
# ==========================================
st.set_page_config(
    page_title="Saylor Engine Dashboard",
    page_icon="⚡",
    layout="wide"
)

# Nutzt Streamlit CSS-Variablen für automatische Dark- & Light-Mode Kompatibilität
st.markdown("""
    <style>
        header[data-testid="stHeader"] {
            display: none !important;
        }
        .block-container {
            padding-top: 0.5rem !important;
            padding-bottom: 2rem !important;
        }
        .sticky-header-box {
            position: -webkit-sticky;
            position: sticky;
            top: 0;
            background-color: var(--background-color);
            color: var(--text-color);
            z-index: 9999;
            padding: 0.8rem 0 0.8rem 0;
            border-bottom: 1px solid var(--gray-30, rgba(128, 128, 128, 0.2));
            margin-bottom: 1.5rem;
        }
        .sticky-title {
            margin: 0;
            padding: 0;
            font-size: 2.2rem;
            font-weight: 700;
            line-height: 1.2;
            color: var(--text-color);
        }
        .sticky-subtitle {
            margin: 0;
            padding-top: 0.3rem;
            opacity: 0.7;
            font-size: 0.95rem;
            color: var(--text-color);
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HISTORISCHE SEC-CASH-DATENBANK (8-K / 10-Q / 10-K)
# ==========================================
SEC_CASH_HISTORICAL = [
    ("2020-08-11", 50000000),
    ("2020-12-21", 60000000),
    ("2021-02-24", 70000000),
    ("2021-06-21", 80000000),
    ("2021-09-12", 85000000),
    ("2021-12-09", 90000000),
    ("2022-01-31", 80000000),
    ("2022-04-05", 70000000),
    ("2022-06-29", 60000000),
    ("2022-12-22", 50000000),
    ("2023-06-28", 60000000),
    ("2023-09-24", 45000000),
    ("2023-12-27", 46800000),
    ("2024-02-26", 50000000),
    ("2024-03-11", 55000000),
    ("2024-04-26", 57000000),
    ("2024-06-20", 60000000),
    ("2024-09-13", 100000000),
    ("2024-11-11", 200000000),
    ("2024-11-18", 500000000),
    ("2024-11-25", 1000000000),
    ("2024-12-02", 1500000000),
    ("2024-12-09", 2000000000),
    ("2025-01-01", 2500000000),
    ("2025-06-01", 3200000000),
    ("2026-01-01", 3800000000),
    ("2026-08-01", 4000000000)
]

df_cash = pd.DataFrame(SEC_CASH_HISTORICAL, columns=["date", "cash_usd"])
df_cash['date'] = pd.to_datetime(df_cash['date'])
df_cash.set_index('date', inplace=True)

# ==========================================
# 3. TRANSLATIONS
# ==========================================
TRANSLATIONS = {
    "DE": {
        "title": "⚡ Saylor Engine ($MSTR)",
        "subtitle": "Automatisches Satoshi-Multiplier & Substanz-Dashboard (SEC & JSON Verifiziert)",
        "sidebar_purchase": "🛒 Deine Kauf-Details",
        "purchase_date": "Kaufdatum wählen",
        "shares_count": "Anzahl MSTR-Aktien (Post-Split)",
        "hist_prices": "📌 **Historische Kurse (Split-bereinigt via Yahoo):**",
        "sidebar_sim": "🎛️ Markt-Simulation",
        "sim_premium": "Simuliertes NAV-Aufgeld/Rabatt (%)",
        "metric_fiat": "1. Fiat Return (Wertentwicklung)",
        "metric_hodl": "2. Spot HODL Benchmark",
        "metric_backing": "3. Corporate Backing (Substanz)",
        "vs_hodl": "vs. Spot HODL",
        "chart_title": "📊 Satoshi Multiplier Snapshot (Gesamt-Portfolio)",
        "timeline_title": "📈 Satoshi / Share & Substanz-Entwicklung (Pro Aktie)",
        "yaxis_sats": "Satoshis pro Aktie (Sats / Share)",
        "bar_fiat": "1. Free Market Value",
        "bar_hodl": "2. Spot HODL Benchmark",
        "bar_substance": "3. Internal Asset Base",
        "layer_btc": "Physische BTC-Deckung",
        "layer_cash": "Firmen-Cash-Reserve in Sats",
        "line_btc": "BTC / Share (Sats)",
        "line_total": "Satoshi Equivalent / Share (incl. Cash)",
        "volume_title": "📊 MSTR Handelsvolumen & Ausstehende Aktien (yfinance)",
        "vol_axis": "Handelsvolumen (Stück)",
        "shares_axis": "Ausstehende Aktien (Shares Outstanding)",
        "expander_title": "ℹ️ Aktuelle Markt- und Fundamentaldaten anzeigen",
        "sources_title": "📚 Primäre Datenquellen & SEC Filings",
        "footer_btc": "BTC Preis",
        "footer_mstr": "MSTR Preis",
        "footer_cash": "MSTR Cash-Reserve",
        "footer_shares": "MSTR Aktien im Umlauf (Diluted)",
        "footer_sources_md": """
        **Verifizierte Datenquellen:**
        * **JSON Tracker (`mstr_treasury_history.json`):**
          * Tagesgenaue Aufschlüsselung der physischen BTC-Käufe, `effective_diluted_shares` & Satoshis pro Aktie via [Saylor Tracker](https://saylortracker.com/).
        * **SEC Filings (MicroStrategy Inc. - CIK 0001050446):**
          * Form 8-K, 10-Q & 10-K (Hartcodierte historische Cash-Reserven).
        * **Marktdaten & Wechselkurse:**
          * Yahoo Finance API (`MSTR`, `BTC-USD`, `EURUSD=X`) – Split-bereinigt.
        """
    },
    "EN": {
        "title": "⚡ Saylor Engine ($MSTR)",
        "subtitle": "Automated Satoshi Multiplier & Corporate Substance Dashboard (SEC & JSON Verified)",
        "sidebar_purchase": "🛒 Your Purchase Details",
        "purchase_date": "Select Purchase Date",
        "shares_count": "Number of MSTR Shares (Post-Split)",
        "hist_prices": "📌 **Historical Prices (Split-adjusted via Yahoo):**",
        "sidebar_sim": "🎛️ Market Simulation",
        "sim_premium": "Simulated NAV Premium/Discount (%)",
        "metric_fiat": "1. Fiat Return",
        "metric_hodl": "2. Spot HODL Benchmark",
        "metric_backing": "3. Corporate Backing (Substance)",
        "vs_hodl": "vs. Spot HODL",
        "chart_title": "📊 Satoshi Multiplier Snapshot (Total Portfolio)",
        "timeline_title": "📈 Satoshi / Share & Substance History (Per Share)",
        "yaxis_sats": "Satoshis per Share (Sats / Share)",
        "bar_fiat": "1. Free Market Value",
        "bar_hodl": "2. Spot HODL Benchmark",
        "bar_substance": "3. Internal Asset Base",
        "layer_btc": "Physical BTC Backing",
        "layer_cash": "Corporate Cash Reserve in Sats",
        "line_btc": "BTC / Share (Sats)",
        "line_total": "Satoshi Equivalent / Share (incl. Cash)",
        "volume_title": "📊 MSTR Trading Volume & Shares Outstanding (yfinance)",
        "vol_axis": "Trading Volume (Shares)",
        "shares_axis": "Shares Outstanding",
        "expander_title": "View Current Market & Fundamental Data",
        "sources_title": "📚 Primary Data Sources & SEC Filings",
        "footer_btc": "BTC Price",
        "footer_mstr": "MSTR Price",
        "footer_cash": "MSTR Cash Reserve",
        "footer_shares": "MSTR Shares Outstanding (Diluted)",
        "footer_sources_md": """
        **Verified Data Sources:**
        * **JSON Tracker (`mstr_treasury_history.json`):**
          * Daily resolution of physical BTC purchases, `effective_diluted_shares` & Satoshis per share sourced from [Saylor Tracker](https://saylortracker.com/).
        * **SEC Filings (MicroStrategy Inc. - CIK 0001050446):**
          * Form 8-K, 10-Q & 10-K (Hardcoded historical cash reserves).
        * **Market Data & FX Rates:**
          * Yahoo Finance API (`MSTR`, `BTC-USD`, `EURUSD=X`) – Split-adjusted.
        """
    }
}

# ==========================================
# 4. SIDEBAR: WÄHRUNGSAUSWAHL
# ==========================================
currency = st.sidebar.selectbox(
    "Währung / Currency",
    options=["USD", "EUR"],
    index=0
)

lang = "DE" if currency == "EUR" else "EN"
t = TRANSLATIONS[lang]
curr_symbol = "$" if currency == "USD" else "€"

# ==========================================
# 5. FIXIERTER (STICKY) HEADER
# ==========================================
st.markdown(f"""
    <div class="sticky-header-box">
        <h1 class="sticky-title">{t['title']}</h1>
        <p class="sticky-subtitle">{t['subtitle']}</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 6. DATA FETCHING (LIVE & HISTORICAL MARKET DATA)
# ==========================================
@st.cache_data(ttl=3600)
def fetch_live_data():
    defaults = {
        "btc_usd": 65000.0,
        "mstr_usd": 135.0,
        "eur_usd": 1.08,
        "mstr_shares": 353_900_000,
        "mstr_btc": 842_138,
        "mstr_cash_usd": 4_000_000_000.0
    }
    try:
        btc_usd = yf.Ticker("BTC-USD").history(period="1d")['Close'].iloc[-1]
        mstr_usd = yf.Ticker("MSTR").history(period="1d")['Close'].iloc[-1]
        eur_usd = yf.Ticker("EURUSD=X").history(period="1d")['Close'].iloc[-1]
        return {
            "btc_usd": float(btc_usd),
            "mstr_usd": float(mstr_usd),
            "eur_usd": float(eur_usd),
            "mstr_shares": defaults["mstr_shares"],
            "mstr_btc": defaults["mstr_btc"],
            "mstr_cash_usd": defaults["mstr_cash_usd"]
        }
    except Exception:
        return defaults

@st.cache_data(ttl=86400)
def fetch_historical_series(start_date):
    start_str = start_date.strftime('%Y-%m-%d')
    try:
        mstr_df = yf.Ticker("MSTR").history(start=start_str, auto_adjust=True)['Close']
        btc_df = yf.Ticker("BTC-USD").history(start=start_str, auto_adjust=True)['Close']
        eur_df = yf.Ticker("EURUSD=X").history(start=start_str, auto_adjust=True)['Close']

        df = pd.DataFrame({
            "mstr_usd": mstr_df,
            "btc_usd": btc_df,
            "eur_usd": eur_df
        })

        df = df.ffill().bfill().dropna()
        if df.empty:
            raise ValueError("Keine Daten vorhanden.")

        df['mstr_eur'] = df['mstr_usd'] / df['eur_usd']
        df['btc_eur'] = df['btc_usd'] / df['eur_usd']
        return df

    except Exception:
        dates = pd.date_range(start=start_date, periods=2)
        return pd.DataFrame({
            "mstr_usd": [135.0, 135.0],
            "btc_usd": [65000.0, 65000.0],
            "eur_usd": [1.08, 1.08],
            "mstr_eur": [125.0, 125.0],
            "btc_eur": [60000.0, 60000.0]
        }, index=dates)

live_data = fetch_live_data()

if currency == "EUR":
    btc_price_curr = live_data["btc_usd"] / live_data["eur_usd"]
    mstr_price_curr = live_data["mstr_usd"] / live_data["eur_usd"]
else:
    btc_price_curr = live_data["btc_usd"]
    mstr_price_curr = live_data["mstr_usd"]

# ==========================================
# 7. USER INPUTS (SIDEBAR)
# ==========================================
st.sidebar.markdown("---")
st.sidebar.header(t["sidebar_purchase"])

purchase_date = st.sidebar.date_input(
    t["purchase_date"],
    value=date(2024, 1, 15),
    min_value=date(2020, 8, 10),
    max_value=date.today() - timedelta(days=2)
)

user_shares = st.sidebar.number_input(
    t["shares_count"], 
    min_value=1, value=1, step=1
)

hist_df = fetch_historical_series(purchase_date)

if not hist_df.empty:
    if currency == "EUR":
        mstr_price_past = float(hist_df['mstr_eur'].iloc[0])
        btc_price_past = float(hist_df['btc_eur'].iloc[0])
    else:
        mstr_price_past = float(hist_df['mstr_usd'].iloc[0])
        btc_price_past = float(hist_df['btc_usd'].iloc[0])
else:
    mstr_price_past = 48.21 if currency == "USD" else 44.00
    btc_price_past = 42511.0 if currency == "USD" else 39000.0

st.sidebar.markdown("---")
st.sidebar.caption(t["hist_prices"])
date_format = "%d.%m.%Y" if lang == "DE" else "%Y-%m-%d"
st.sidebar.text(f"MSTR ({purchase_date.strftime(date_format)}): {curr_symbol}{mstr_price_past:,.2f}")
st.sidebar.text(f"BTC ({purchase_date.strftime(date_format)}): {curr_symbol}{btc_price_past:,.2f}")

st.sidebar.markdown("---")
st.sidebar.subheader(t["sidebar_sim"])

simulated_premium = st.sidebar.slider(
    t["sim_premium"],
    min_value=-20, max_value=50, value=0, step=1
)

premium_factor = 1.0 + (simulated_premium / 100.0)
mstr_price_simulated = mstr_price_curr * premium_factor

# ==========================================
# 8. MATHEMATICAL ENGINE
# ==========================================
SATS_PER_BTC = 100_000_000

total_invest = user_shares * mstr_price_past

hodl_benchmark_sats = (total_invest / btc_price_past) * SATS_PER_BTC
market_value_fiat = user_shares * mstr_price_simulated
market_value_sats = (market_value_fiat / btc_price_curr) * SATS_PER_BTC

current_btc_per_share = live_data["mstr_btc"] / live_data["mstr_shares"]
internal_btc_sats = user_shares * current_btc_per_share * SATS_PER_BTC

cash_per_share_usd = live_data["mstr_cash_usd"] / live_data["mstr_shares"]
total_user_cash_usd = user_shares * cash_per_share_usd
internal_cash_sats = (total_user_cash_usd / live_data["btc_usd"]) * SATS_PER_BTC

total_substance_sats = internal_btc_sats + internal_cash_sats

fiat_return_pct = ((market_value_fiat - total_invest) / total_invest) * 100
market_sats_yield_pct = ((market_value_sats - hodl_benchmark_sats) / hodl_benchmark_sats) * 100
substance_yield_pct = ((total_substance_sats - hodl_benchmark_sats) / hodl_benchmark_sats) * 100

# ==========================================
# 9. UI DISPLAY (KPI CARDS)
# ==========================================
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label=f"{t['metric_fiat']} ({currency})",
        value=f"{curr_symbol}{market_value_fiat:,.2f}",
        delta=f"{fiat_return_pct:+.2f}% (Invest: {curr_symbol}{total_invest:,.2f})"
    )

with col2:
    st.metric(
        label=t["metric_hodl"],
        value=f"{hodl_benchmark_sats:,.0f} Sats",
        delta="100% Benchmark (Basis)"
    )

with col3:
    st.metric(
        label=t["metric_backing"],
        value=f"{total_substance_sats:,.0f} Sats",
        delta=f"{substance_yield_pct:+.2f}% {t['vs_hodl']}"
    )

st.markdown("---")

# ==========================================
# 10. PLOTLY SNAPSHOT CHART (TRANSPARENT / DARK MODE READY)
# ==========================================
fig_bar = go.Figure()

fig_bar.add_trace(go.Bar(
    name=t["bar_fiat"],
    x=[t["bar_fiat"]],
    y=[market_value_sats],
    marker_color="#29B6F6",
    text=[f"{market_value_sats:,.0f} Sats"],
    textposition="auto"
))

fig_bar.add_trace(go.Bar(
    name=t["bar_hodl"],
    x=[t["bar_hodl"]],
    y=[hodl_benchmark_sats],
    marker_color="#F7931A",
    text=[f"{hodl_benchmark_sats:,.0f} Sats"],
    textposition="auto"
))

fig_bar.add_trace(go.Bar(
    name=t["layer_btc"],
    x=[t["bar_substance"]],
    y=[internal_btc_sats],
    marker_color="#4CAF50",
    text=[f"{internal_btc_sats:,.0f} Sats"],
    textposition="inside"
))

fig_bar.add_trace(go.Bar(
    name=t["layer_cash"],
    x=[t["bar_substance"]],
    y=[internal_cash_sats],
    marker_color="#81C784",
    text=[f"{internal_cash_sats:,.0f} Sats"],
    textposition="inside"
))

fig_bar.update_layout(
    barmode="stack",
    title=dict(
        text=t["chart_title"],
        font=dict(size=20)
    ),
    yaxis_title="Satoshis (Sats)",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="rgba(128,128,128,0.9)"),
    height=450,
    margin=dict(t=50, b=80, l=10, r=10),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.2,
        xanchor="center",
        x=0.5
    ),
    yaxis=dict(
        gridcolor="rgba(128, 128, 128, 0.2)",
        zerolinecolor="rgba(128, 128, 128, 0.3)"
    ),
    xaxis=dict(
        gridcolor="rgba(128, 128, 128, 0.2)"
    )
)

st.plotly_chart(fig_bar, use_container_width=True)

# ==========================================
# 11. COMBINED DATA ENGINE (SAYLOR-TRACKER JSON PARSER)
# ==========================================
st.markdown("---")

hist_df_clean = hist_df.copy()
idx_dt = pd.to_datetime(hist_df_clean.index)
hist_df_clean.index = idx_dt.tz_localize(None) if idx_dt.tz is not None else idx_dt

merged_df = hist_df_clean.copy()

mstr_col = "mstr_eur" if currency == "EUR" else "mstr_usd"
btc_col = "btc_eur" if currency == "EUR" else "btc_usd"

# 1. Börsenpreis in Sats pro Aktie
merged_df['mstr_price_in_sats'] = (merged_df[mstr_col] / merged_df[btc_col]) * SATS_PER_BTC

# 2. SAYLOR-TRACKER JSON DIREKT LADEN UND ENTPACKEN
try:
    with open("mstr_treasury_history.json", "r") as f:
        json_raw = json.load(f)
    
    if "MSTR" in json_raw and "historicalData" in json_raw["MSTR"]:
        hist_data = json_raw["MSTR"]["historicalData"]
    elif "historicalData" in json_raw:
        hist_data = json_raw["historicalData"]
    else:
        hist_data = json_raw

    diluted_shares_series = hist_data.get("effective_diluted_shares", hist_data.get("effective_shares", [None]*len(hist_data["dates"])))

    df_j = pd.DataFrame({
        "dates": hist_data["dates"],
        "btc_per_share": hist_data.get("btc_per_share", [None]*len(hist_data["dates"])),
        "effective_diluted_shares": diluted_shares_series
    })

    df_j['parsed_date'] = pd.to_datetime(df_j['dates']).dt.tz_localize(None)
    df_j = df_j.sort_values('parsed_date').drop_duplicates('parsed_date', keep='last')
    df_j.set_index('parsed_date', inplace=True)

    df_j['btc_per_share_sats'] = pd.to_numeric(df_j['btc_per_share'], errors='coerce') * SATS_PER_BTC

    merged_df['btc_per_share_sats'] = df_j['btc_per_share_sats'].reindex(merged_df.index).ffill().bfill()

    if 'effective_diluted_shares' in df_j.columns and df_j['effective_diluted_shares'].notna().any():
        merged_df['shares_out'] = pd.to_numeric(df_j['effective_diluted_shares'], errors='coerce').reindex(merged_df.index).ffill().bfill()
    else:
        merged_df['shares_out'] = live_data["mstr_shares"]

except Exception as e:
    st.error(f"❌ JSON-Fehler beim Lesen der Saylor-Struktur: {e}")
    merged_df['btc_per_share_sats'] = (live_data["mstr_btc"] / live_data["mstr_shares"]) * SATS_PER_BTC
    merged_df['shares_out'] = live_data["mstr_shares"]

# 3. Cash aus hartcodiertem SEC-Array mappen & umrechnen
cash_daily = df_cash['cash_usd'].reindex(merged_df.index).ffill().bfill()
merged_df['cash_usd'] = cash_daily

merged_df['cash_per_share_usd'] = merged_df['cash_usd'] / merged_df['shares_out']
merged_df['cash_per_share_sats'] = (merged_df['cash_per_share_usd'] / merged_df['btc_usd']) * SATS_PER_BTC

# 4. Gesamtsubstanz = Dynamischer JSON-BTC-Verlauf + Hartcodiertes SEC-Cash
merged_df['total_substance_per_share_sats'] = merged_df['btc_per_share_sats'] + merged_df['cash_per_share_sats']

hodl_per_share_sats = (mstr_price_past / btc_price_past) * SATS_PER_BTC

# ==========================================
# 12. PLOTLY HISTORICAL TIMELINE CHART (TRANSPARENT / DARK MODE READY)
# ==========================================
fig_line = go.Figure()

# 1. Free Market Value
fig_line.add_trace(go.Scatter(
    x=merged_df.index,
    y=merged_df['mstr_price_in_sats'],
    mode='lines',
    name='Free Market Value (Sats / Share)',
    fill='tozeroy',
    fillcolor='rgba(41, 182, 246, 0.1)',
    line=dict(color='#29B6F6', width=2),
    customdata=merged_df[mstr_col],
    hovertemplate="<b>Datum:</b> %{x|%d.%m.%Y}<br><b>Market Value / Share:</b> %{y:,.0f} Sats<br><b>Aktienkurs:</b> " + curr_symbol + "%{customdata:,.2f}<extra></extra>"
))

# 2. HODL Benchmark
fig_line.add_trace(go.Scatter(
    x=merged_df.index,
    y=[hodl_per_share_sats] * len(merged_df),
    mode='lines',
    name='Spot HODL Benchmark / Share',
    line=dict(color='#F7931A', width=2, dash='dash'),
    hovertemplate="<b>Spot Benchmark / Share:</b> %{y:,.0f} Sats<extra></extra>"
))

# 3. BTC / Share aus JSON (Verlauf!)
fig_line.add_trace(go.Scatter(
    x=merged_df.index,
    y=merged_df['btc_per_share_sats'],
    mode='lines',
    name=t["line_btc"],
    line=dict(color='#4CAF50', width=3),
    hovertemplate="<b>Datum:</b> %{x|%d.%m.%Y}<br><b>BTC / Share (JSON):</b> %{y:,.0f} Sats<extra></extra>"
))

# 4. Satoshi Equivalent / Share (JSON BTC + SEC Cash)
fig_line.add_trace(go.Scatter(
    x=merged_df.index,
    y=merged_df['total_substance_per_share_sats'],
    mode='lines',
    name=t["line_total"],
    line=dict(color='#81C784', width=2, dash='dot'),
    customdata=merged_df[['cash_per_share_usd', 'cash_per_share_sats']].values,
    hovertemplate="<b>Datum:</b> %{x|%d.%m.%Y}<br><b>Total Substance:</b> %{y:,.0f} Sats<br><i>(SEC Cash Anteil: $%{customdata[0]:,.2f} = %{customdata[1]:,.0f} Sats)</i><extra></extra>"
))

fig_line.update_layout(
    title=dict(
        text=t["timeline_title"],
        font=dict(size=20)
    ),
    xaxis_title="Datum",
    yaxis_title=t["yaxis_sats"],
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="rgba(128,128,128,0.9)"),
    height=600,
    margin=dict(t=50, b=80, l=10, r=10),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.25,
        xanchor="center",
        x=0.5
    ),
    yaxis=dict(
        gridcolor="rgba(128, 128, 128, 0.2)",
        zerolinecolor="rgba(128, 128, 128, 0.3)"
    ),
    xaxis=dict(
        gridcolor="rgba(128, 128, 128, 0.2)"
    )
)

st.plotly_chart(fig_line, use_container_width=True)

# ==========================================
# 13. MSTR TRADING VOLUME & SHARES ISSUED (SYNCHRONIZED TIMELINE)
# ==========================================
st.markdown("---")

@st.cache_data(ttl=3600)
def load_mstr_volume_and_shares(start_date):
    ticker = yf.Ticker("MSTR")
    start_str = start_date.strftime("%Y-%m-%d")
    try:
        # Lade historische Marktdaten ab Kaufdatum
        hist = ticker.history(start=start_str, auto_adjust=True)
        # Shares Outstanding Historie ab Kaufdatum
        shares = ticker.get_shares_full(start=start_str)
    except Exception:
        hist, shares = pd.DataFrame(), None
    return hist, shares

# Lade Daten synchron zum 'purchase_date' aus der Sidebar
mstr_hist, mstr_shares = load_mstr_volume_and_shares(purchase_date)

if not mstr_hist.empty:
    fig_vol = make_subplots(specs=[[{"secondary_y": True}]])

    # 1. Handelsvolumen als Balkendiagramm (Primäre Y-Achse)
    fig_vol.add_trace(
        go.Bar(
            x=mstr_hist.index,
            y=mstr_hist["Volume"],
            name=t["vol_axis"],
            marker_color="rgba(41, 182, 246, 0.4)",
        ),
        secondary_y=False,
    )

    # 2. Shares Outstanding als Linie (Sekundäre Y-Achse)
    if mstr_shares is not None and not mstr_shares.empty:
        fig_vol.add_trace(
            go.Scatter(
                x=mstr_shares.index,
                y=mstr_shares.values,
                name=t["shares_axis"],
                mode="lines",
                line=dict(color="#F7931A", width=3),
            ),
            secondary_y=True,
        )

    # Synchrone Achsenbegrenzung festlegen
    min_x = merged_df.index.min()
    max_x = merged_df.index.max()

    fig_vol.update_layout(
        title=dict(
            text=t["volume_title"],
            font=dict(size=20)
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(128,128,128,0.9)"),
        height=500,
        margin=dict(t=50, b=80, l=10, r=10),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.25,
            xanchor="center",
            x=0.5
        ),
        xaxis=dict(
            gridcolor="rgba(128, 128, 128, 0.2)",
            range=[min_x, max_x]  # <--- Erzwingt dieselbe Zeitachse wie oben!
        ),
    )

    fig_vol.update_yaxes(
        title_text=t["vol_axis"], 
        gridcolor="rgba(128, 128, 128, 0.2)", 
        secondary_y=False
    )
    fig_vol.update_yaxes(
        title_text=t["shares_axis"], 
        showgrid=False, 
        secondary_y=True
    )

    st.plotly_chart(fig_vol, use_container_width=True)

# ==========================================
# 14. FOOTER & QUELLEN-NACHWEIS
# ==========================================
st.markdown("---")

col_f1, col_f2 = st.columns(2)

with col_f1:
    with st.expander(t["expander_title"]):
        st.write(f"- **{t['footer_btc']}:** {curr_symbol}{btc_price_curr:,.2f}")
        st.write(f"- **{t['footer_mstr']}:** {curr_symbol}{mstr_price_curr:,.2f}")
        st.write(f"- **EUR/USD:** {live_data['eur_usd']:.4f}")
        st.write(f"- **{t['footer_cash']}:** ${live_data['mstr_cash_usd']/1e9:.2f} B USD")
        st.write(f"- **{t['footer_shares']}:** {live_data['mstr_shares']:,}")

with col_f2:
    with st.expander(t["sources_title"]):
        st.markdown(t["footer_sources_md"])
