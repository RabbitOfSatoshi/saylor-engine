import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
from datetime import date, timedelta
import pandas as pd
import json

# ==========================================
# 1. STREAMLIT PAGE CONFIG & CLEAN STICKY CSS
# ==========================================
st.set_page_config(
    page_title="Saylor Engine Dashboard",
    page_icon="⚡",
    layout="wide"
)

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
            background-color: var(--background-color, #ffffff);
            z-index: 9999;
            padding: 0.8rem 0 0.8rem 0;
            border-bottom: 1px solid rgba(49, 51, 63, 0.1);
            margin-bottom: 1.5rem;
        }
        .sticky-title {
            margin: 0;
            padding: 0;
            font-size: 2.2rem;
            font-weight: 700;
            line-height: 1.2;
        }
        .sticky-subtitle {
            margin: 0;
            padding-top: 0.3rem;
            color: #666;
            font-size: 0.95rem;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HISTORISCHE SEC-DATENBANK
# ==========================================
JSON_FILENAME = "mstr_treasury_history.json"

try:
    with open(JSON_FILENAME, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    if isinstance(json_data, dict):
        if "MSTR" in json_data and "historicalData" in json_data["MSTR"]:
            hist_node = json_data["MSTR"]["historicalData"]
        elif "historicalData" in json_data:
            hist_node = json_data["historicalData"]
        else:
            hist_node = json_data
    else:
        hist_node = json_data

    df_tx = pd.DataFrame(hist_node)

    column_mapping = {
        'dates': 'date',
        'btc_balance': 'btc_holdings',
        'total_outstanding_shares': 'shares_out',
        'cash_balance': 'cash_usd'
    }
    df_tx.rename(columns=column_mapping, inplace=True)

    df_tx['date'] = pd.to_datetime(df_tx['date'])
    df_tx.set_index('date', inplace=True)

    if 'shares_out' not in df_tx.columns or df_tx['shares_out'].dropna().empty:
        df_tx['shares_out'] = 353_900_000
    else:
        df_tx['shares_out'] = df_tx['shares_out'].ffill().bfill()

    if 'cash_usd' not in df_tx.columns or df_tx['cash_usd'].dropna().empty:
        df_tx['cash_usd'] = 4_000_000_000
    else:
        df_tx['cash_usd'] = df_tx['cash_usd'].ffill().bfill()

    df_tx['btc_holdings'] = df_tx['btc_holdings'].ffill().bfill()

except FileNotFoundError:
    st.error(f"Datei '{JSON_FILENAME}' wurde nicht gefunden!")
    st.stop()
except Exception as e:
    st.error(f"Fehler beim Verarbeiten der JSON-Datei: {e}")
    st.stop()

# ==========================================
# 3. TRANSLATIONS
# ==========================================
TRANSLATIONS = {
    "DE": {
        "title": "⚡ Saylor Engine ($MSTR)",
        "subtitle": "Automatisches Satoshi-Multiplier & Substanz-Dashboard (SEC-Verifiziert)",
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
        "bar_fiat": "1. Free Market Value",
        "bar_hodl": "2. Spot HODL Benchmark",
        "bar_substance": "3. Internal Asset Base",
        "layer_btc": "Physical BTC Backing",
        "layer_cash": "Corporate Cash Reserve in Sats",
        "line_btc": "BTC / Share (Sats)",
        "line_total": "Satoshi Equivalent / Share (incl. Cash)",
        "expander_title": "ℹ️ Aktuelle Markt- und Fundamentaldaten anzeigen",
        "sources_title": "📚 Primäre Datenquellen & SEC Filings",
        "footer_btc": "BTC Preis",
        "footer_mstr": "MSTR Preis",
        "footer_cash": "MSTR Cash-Reserve",
        "footer_shares": "MSTR Aktien im Umlauf",
        "footer_sources_md": """
        **Verifizierte Datenquellen:**
        * **SEC Filings (MicroStrategy Inc. - CIK 0001050446):**
          * Dynamisch geladen aus `mstr_treasury_history.json` (Form 8-K, 10-Q & 10-K)
        * **Marktdaten & Wechselkurse:**
          * Yahoo Finance API (`MSTR`, `BTC-USD`, `EURUSD=X`) – Split-bereinigt.
        """
    },
    "EN": {
        "title": "⚡ Saylor Engine ($MSTR)",
        "subtitle": "Automated Satoshi Multiplier & Corporate Substance Dashboard (SEC Verified)",
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
        "bar_fiat": "1. Free Market Value",
        "bar_hodl": "2. Spot HODL Benchmark",
        "bar_substance": "3. Internal Asset Base",
        "layer_btc": "Physical BTC Backing",
        "layer_cash": "Corporate Cash Reserve in Sats",
        "line_btc": "BTC / Share (Sats)",
        "line_total": "Satoshi Equivalent / Share (incl. Cash)",
        "expander_title": "View Current Market & Fundamental Data",
        "sources_title": "📚 Primary Data Sources & SEC Filings",
        "footer_btc": "BTC Price",
        "footer_mstr": "MSTR Price",
        "footer_cash": "MSTR Cash Reserve",
        "footer_shares": "MSTR Shares Outstanding",
        "footer_sources_md": """
        **Verified Data Sources:**
        * **SEC Filings (MicroStrategy Inc. - CIK 0001050446):**
          * Dynamically loaded from `mstr_treasury_history.json` (Form 8-K, 10-Q & 10-K)
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
# 6. DATA FETCHING (LIVE & HISTORICAL)
# ==========================================
@st.cache_data(ttl=3600)
def fetch_live_data():
    latest_sec = df_tx.iloc[-1]
    defaults = {
        "btc_usd": 65000.0,
        "mstr_usd": 135.0,
        "eur_usd": 1.08,
        "mstr_shares": int(latest_sec.get('shares_out', 353_900_000)),
        "mstr_btc": float(latest_sec.get('btc_holdings', 842_138)),
        "mstr_cash_usd": float(latest_sec.get('cash_usd', 4_000_000_000))
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
    value=date(2024, 2, 28),
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
    mstr_price_past = 68.50 if currency == "USD" else 63.00
    btc_price_past = 59000.0 if currency == "USD" else 54000.0

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

# Step 1: HODL Benchmark
hodl_benchmark_sats = (total_invest / btc_price_past) * SATS_PER_BTC

# Step 2: Free Market Today
market_value_fiat = user_shares * mstr_price_simulated
market_value_sats = (market_value_fiat / btc_price_curr) * SATS_PER_BTC

# Step 3: Saylor Engine (Internal BTC)
current_btc_per_share = live_data["mstr_btc"] / live_data["mstr_shares"]
internal_btc_sats = user_shares * current_btc_per_share * SATS_PER_BTC

# Step 4: Cash-to-Sats
cash_per_share_usd = live_data["mstr_cash_usd"] / live_data["mstr_shares"]
total_user_cash_usd = user_shares * cash_per_share_usd
internal_cash_sats = (total_user_cash_usd / live_data["btc_usd"]) * SATS_PER_BTC

# Step 5: Total Substance
total_substance_sats = internal_btc_sats + internal_cash_sats

# Renditen
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
# 10. PLOTLY SNAPSHOT CHART
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
        font=dict(size=20, color="#31333F", family="Source Sans Pro, sans-serif")
    ),
    yaxis_title="Satoshis (Sats)",
    template="plotly_white",
    height=500,
    margin=dict(t=50, b=80, l=10, r=10),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.2,
        xanchor="center",
        x=0.5
    )
)

st.plotly_chart(fig_bar, use_container_width=True)

# ==========================================
# 11. HISTORICAL TIMELINE ENGINE (EXAKT PRO AKTIE CALCULATED)
# ==========================================
st.markdown("---")

hist_df_clean = hist_df.copy()
hist_df_clean.index = pd.to_datetime(hist_df_clean.index).tz_localize(None)

treasury_daily = df_tx.reindex(
    hist_df_clean.index.union(df_tx.index)
).ffill().reindex(hist_df_clean.index)

first_btc = df_tx['btc_holdings'].iloc[0] if not df_tx.empty else 21454
first_shares = df_tx['shares_out'].iloc[0] if not df_tx.empty else 96000000
first_cash = df_tx['cash_usd'].iloc[0] if not df_tx.empty else 0

treasury_daily['btc_holdings'] = treasury_daily['btc_holdings'].fillna(first_btc)
treasury_daily['shares_out'] = treasury_daily['shares_out'].fillna(first_shares)
treasury_daily['cash_usd'] = treasury_daily['cash_usd'].fillna(first_cash)

merged_df = hist_df_clean.copy()
merged_df['btc_holdings'] = treasury_daily['btc_holdings']
merged_df['shares_out'] = treasury_daily['shares_out']
merged_df['cash_usd'] = treasury_daily['cash_usd']

mstr_col = "mstr_eur" if currency == "EUR" else "mstr_usd"
btc_col = "btc_eur" if currency == "EUR" else "btc_usd"

# 1. Börsenpreis der Aktie in Satoshis (pro Aktie)
merged_df['mstr_price_in_sats'] = (merged_df[mstr_col] / merged_df[btc_col]) * SATS_PER_BTC

# 2. Reine BTC pro Aktie (in Satoshis)
merged_df['btc_per_share_sats'] = (merged_df['btc_holdings'] / merged_df['shares_out']) * SATS_PER_BTC

# 3. Cash pro Aktie umgerechnet in USD -> Satoshis an Tag X
merged_df['cash_per_share_usd'] = merged_df['cash_usd'] / merged_df['shares_out']
merged_df['cash_per_share_sats'] = (merged_df['cash_per_share_usd'] / merged_df['btc_usd']) * SATS_PER_BTC

# 4. Gesamtes Satoshi-Äquivalent pro Aktie (BTC + Cash)
merged_df['total_substance_per_share_sats'] = merged_df['btc_per_share_sats'] + merged_df['cash_per_share_sats']

# HODL Benchmark PRO AKTIE (relativ zum Kaufdatum)
hodl_per_share_sats = (mstr_price_past / btc_price_past) * SATS_PER_BTC

# ==========================================
# 12. PLOTLY HISTORICAL TIMELINE CHART (PRO AKTIE)
# ==========================================
fig_line = go.Figure()

# 1. Börsenwert der Aktie in Sats
fig_line.add_trace(go.Scatter(
    x=merged_df.index,
    y=merged_df['mstr_price_in_sats'],
    mode='lines',
    name='Free Market Value (Sats / Share)',
    fill='tozeroy',
    fillcolor='rgba(41, 182, 246, 0.08)',
    line=dict(color='#29B6F6', width=2),
    customdata=merged_df[mstr_col],
    hovertemplate="<b>Datum:</b> %{x|%d.%m.%Y}<br><b>Market Value / Share:</b> %{y:,.0f} Sats<br><b>Aktienkurs:</b> " + curr_symbol + "%{customdata:,.2f}<extra></extra>"
))

# 2. Spot HODL Benchmark
fig_line.add_trace(go.Scatter(
    x=merged_df.index,
    y=[hodl_per_share_sats] * len(merged_df),
    mode='lines',
    name='Spot HODL Benchmark / Share',
    line=dict(color='#F7931A', width=2, dash='dash'),
    hovertemplate="<b>Spot Benchmark / Share:</b> %{y:,.0f} Sats<extra></extra>"
))

# 3. BTC / Share (Sats)
fig_line.add_trace(go.Scatter(
    x=merged_df.index,
    y=merged_df['btc_per_share_sats'],
    mode='lines',
    name=t["line_btc"],
    line=dict(color='#4CAF50', width=2.5),
    hovertemplate="<b>Datum:</b> %{x|%d.%m.%Y}<br><b>BTC / Share:</b> %{y:,.0f} Sats<extra></extra>"
))

# 4. Satoshi Equivalent / Share (incl. Cash)
fig_line.add_trace(go.Scatter(
    x=merged_df.index,
    y=merged_df['total_substance_per_share_sats'],
    mode='lines',
    name=t["line_total"],
    line=dict(color='#81C784', width=1.5, dash='dot'),
    customdata=merged_df[['cash_per_share_usd', 'cash_per_share_sats']].values,
    hovertemplate="<b>Datum:</b> %{x|%d.%m.%Y}<br><b>Total Substance / Share:</b> %{y:,.0f} Sats<br><i>(davon Cash: $%{customdata[0]:,.2f} = %{customdata[1]:,.0f} Sats)</i><extra></extra>"
))

fig_line.update_layout(
    title=dict(
        text=t["timeline_title"],
        font=dict(size=20, color="#31333F", family="Source Sans Pro, sans-serif")
    ),
    xaxis_title="Datum",
    yaxis_title="Satoshis pro Aktie (Sats / Share)",
    template="plotly_white",
    height=600,
    margin=dict(t=50, b=80, l=10, r=10),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.25,
        xanchor="center",
        x=0.5
    )
)

st.plotly_chart(fig_line, use_container_width=True)

# ==========================================
# 13. FOOTER & QUELLEN-NACHWEIS
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
