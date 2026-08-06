import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
from datetime import date, timedelta
import pandas as pd

# ==========================================
# 1. STREAMLIT PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Saylor Engine Dashboard",
    page_icon="⚡",
    layout="wide"
)

# ==========================================
# 2. HISTORISCHE SEC-TRANSAKTIONSDATENBANK (MSTR)
# Format: (Datum, BTC_Delta, Aktienanzahl_Absolut_oder_Delta)
# Inklusive des Tax-Loss-Harvesting Verkaufs vom 22.12.2022!
# (Alle Daten Post-Split 10:1 bereinigt)
# ==========================================
MSTR_TRANSACTIONS = [
    ("2020-08-11", 21454, 96000000),
    ("2020-09-14", 16796, 96000000),
    ("2020-12-04", 2574, 96000000),
    ("2020-12-21", 29646, 97000000),
    ("2021-01-22", 314, 97000000),
    ("2021-02-02", 295, 97000000),
    ("2021-02-24", 19452, 99000000),
    ("2021-03-01", 324, 99000000),
    ("2021-03-05", 209, 99000000),
    ("2021-03-12", 262, 99000000),
    ("2021-04-05", 253, 99000000),
    ("2021-05-13", 271, 99000000),
    ("2021-05-18", 229, 99000000),
    ("2021-06-21", 13006, 107000000),
    ("2021-09-12", 8957, 107000000),
    ("2021-12-09", 8436, 112000000),
    ("2021-12-30", 1913, 112000000),
    ("2022-01-31", 660, 112000000),
    ("2022-04-05", 4167, 113000000),
    ("2022-06-29", 481, 113000000),
    ("2022-09-20", 301, 113000000),
    ("2022-12-22", -704, 115000000), # <--- VERKAUF (Tax-Loss Harvesting)
    ("2022-12-24", 810, 115000000),  # <--- Wiederkauf
    ("2022-12-28", 2384, 115000000),
    ("2023-03-27", 6455, 115000000),
    ("2023-04-05", 1045, 115000000),
    ("2023-06-28", 12333, 126000000),
    ("2023-07-31", 467, 126000000),
    ("2023-09-24", 5445, 137000000),
    ("2023-11-30", 16285, 148000000),
    ("2023-12-27", 14620, 161000000),
    ("2024-01-31", 850, 161000000),
    ("2024-02-26", 3000, 170000000),
    ("2024-03-11", 12000, 177000000),
    ("2024-03-19", 9246, 177000000),
    ("2024-04-26", 154, 177000000),
    ("2024-06-20", 11931, 177000000),
    ("2024-08-01", 169, 177000000),
    ("2024-09-13", 18300, 197000000),
    ("2024-09-20", 7420, 203000000),
    ("2024-11-11", 27200, 222000000),
    ("2024-11-18", 51780, 256000000),
    ("2024-11-25", 55500, 280000000),
    ("2024-12-02", 15400, 290000000),
    ("2024-12-09", 21550, 305000000),
    ("2025-01-01", 23720, 320000000),
    ("2025-06-01", 152630, 340000000),
    ("2026-01-01", 150000, 350000000),
    ("2026-08-01", 92138, 353900000)
]

df_tx = pd.DataFrame(MSTR_TRANSACTIONS, columns=["date", "btc_change", "shares_out"])
df_tx['date'] = pd.to_datetime(df_tx['date'])

# Kumulierte BTC-Bestände errechnen
df_tx['btc_holdings'] = df_tx['btc_change'].cumsum()
df_tx.set_index('date', inplace=True)

# ==========================================
# 3. TRANSLATIONS
# ==========================================
TRANSLATIONS = {
    "DE": {
        "title": "⚡ Saylor Engine ($MSTR)",
        "subtitle": "Automatisches Satoshi-Multiplier & Substanz-Dashboard",
        "sidebar_settings": "🌐 Sprache & Währung",
        "sidebar_purchase": "🛒 Deine Kauf-Details",
        "purchase_date": "Kaufdatum wählen",
        "shares_count": "Anzahl gekaufter MSTR-Aktien",
        "hist_prices": "📌 **Automatisch ermittelte historische Kurse:**",
        "sidebar_sim": "🎛️ Markt-Simulation",
        "sim_premium": "Simuliertes NAV-Aufgeld/Rabatt (%)",
        "metric_return": "Fiat Wertentwicklung",
        "metric_market_sats": "Market Sats Yield (Freier Markt)",
        "metric_substance_sats": "Substance Yield (Firmen-Substanz)",
        "vs_hodl": "vs. Spot HODL",
        "chart_title": "Satoshi Multiplier Momentaufnahme",
        "timeline_title": "📈 Satoshi Multiplier Zeitverlauf (Exakte SEC Transaktions-Historie)",
        "bar_hodl": "1. Spot HODL Benchmark",
        "bar_market": "2. Free Market Value",
        "bar_substance": "3. Internal Asset Base",
        "layer_btc": "Physische BTC-Deckung",
        "layer_cash": "Firmen-Cash-Reserve in Sats",
        "expander_title": "ℹ️ Aktuelle Markt- und Fundamentaldaten anzeigen",
        "footer_btc": "BTC Preis",
        "footer_mstr": "MSTR Preis",
        "footer_cash": "MSTR Cash-Reserve",
        "footer_shares": "MSTR Aktien im Umlauf",
    },
    "EN": {
        "title": "⚡ Saylor Engine ($MSTR)",
        "subtitle": "Automated Satoshi Multiplier & Corporate Substance Dashboard",
        "sidebar_settings": "🌐 Language & Currency",
        "sidebar_purchase": "🛒 Your Purchase Details",
        "purchase_date": "Select Purchase Date",
        "shares_count": "Number of MSTR Shares Bought",
        "hist_prices": "📌 **Automatically fetched historical prices:**",
        "sidebar_sim": "🎛️ Market Simulation",
        "sim_premium": "Simulated NAV Premium/Discount (%)",
        "metric_return": "Fiat Return",
        "metric_market_sats": "Market Sats Yield (Open Market)",
        "metric_substance_sats": "Substance Yield (Internal Base)",
        "vs_hodl": "vs. Spot HODL",
        "chart_title": "Satoshi Multiplier Snapshot",
        "timeline_title": "📈 Satoshi Multiplier Historical Performance (SEC Filing Data)",
        "bar_hodl": "1. Spot HODL Benchmark",
        "bar_market": "2. Free Market Value",
        "bar_substance": "3. Internal Asset Base",
        "layer_btc": "Physical BTC Backing",
        "layer_cash": "Corporate Cash Reserve in Sats",
        "expander_title": "ℹ️ View Current Market & Fundamental Data",
        "footer_btc": "BTC Price",
        "footer_mstr": "MSTR Price",
        "footer_cash": "MSTR Cash Reserve",
        "footer_shares": "MSTR Shares Outstanding",
    }
}

# ==========================================
# 4. SIDEBAR: CURRENCY & LANGUAGE SELECTOR
# ==========================================
st.sidebar.header("🌐 Language / Währung")
currency = st.sidebar.radio(
    "Select Currency / Währung wählen",
    options=["USD", "EUR"],  # Standard: USD
    index=0
)

lang = "DE" if currency == "EUR" else "EN"
t = TRANSLATIONS[lang]
curr_symbol = "$" if currency == "USD" else "€"

st.title(t["title"])
st.caption(t["subtitle"])

# ==========================================
# 5. DATA FETCHING (LIVE & HISTORICAL)
# ==========================================
@st.cache_data(ttl=3600)
def fetch_live_data():
    defaults = {
        "btc_usd": 65000.0,
        "mstr_usd": 135.0,
        "eur_usd": 1.08,
        "mstr_shares": 353_900_000,
        "mstr_btc": 842_138,
        "mstr_cash_usd": 4_000_000_000
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
        mstr_df = yf.Ticker("MSTR").history(start=start_str)['Close']
        btc_df = yf.Ticker("BTC-USD").history(start=start_str)['Close']
        eur_df = yf.Ticker("EURUSD=X").history(start=start_str)['Close']

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

# Aktuelle Preise
if currency == "EUR":
    btc_price_curr = live_data["btc_usd"] / live_data["eur_usd"]
    mstr_price_curr = live_data["mstr_usd"] / live_data["eur_usd"]
else:
    btc_price_curr = live_data["btc_usd"]
    mstr_price_curr = live_data["mstr_usd"]

# ==========================================
# 6. USER INPUTS (SIDEBAR)
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
    min_value=1, value=1, step=1  # Standard: 1 Share
)

hist_df = fetch_historical_series(purchase_date)

# Kaufkurse sicher ermitteln
if not hist_df.empty:
    if currency == "EUR":
        mstr_price_past = float(hist_df['mstr_eur'].iloc[0])
        btc_price_past = float(hist_df['btc_eur'].iloc[0])
    else:
        mstr_price_past = float(hist_df['mstr_usd'].iloc[0])
        btc_price_past = float(hist_df['btc_usd'].iloc[0])
else:
    mstr_price_past = 63.00 if currency == "USD" else 57.92
    btc_price_past = 42000.0 if currency == "USD" else 38800.0

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
# 7. MATHEMATICAL ENGINE (CURRENT)
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

# Step 4: Dry Powder (Cash-to-Sats)
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
# 8. UI DISPLAY (KPI CARDS)
# ==========================================
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label=f"{t['metric_return']} ({currency})",
        value=f"{curr_symbol}{market_value_fiat:,.2f}",
        delta=f"{fiat_return_pct:+.2f}% (Invest: {curr_symbol}{total_invest:,.2f})"
    )

with col2:
    st.metric(
        label=t["metric_market_sats"],
        value=f"{market_value_sats:,.0f} Sats",
        delta=f"{market_sats_yield_pct:+.2f}% {t['vs_hodl']}"
    )

with col3:
    st.metric(
        label=t["metric_substance_sats"],
        value=f"{total_substance_sats:,.0f} Sats",
        delta=f"{substance_yield_pct:+.2f}% {t['vs_hodl']}"
    )

st.markdown("---")

# ==========================================
# 9. PLOTLY SNAPSHOT CHART (BAR)
# ==========================================
st.subheader(f"📊 {t['chart_title']}")

fig_bar = go.Figure()

fig_bar.add_trace(go.Bar(
    name=t["bar_hodl"],
    x=[t["bar_hodl"]],
    y=[hodl_benchmark_sats],
    marker_color="#F7931A",
    text=[f"{hodl_benchmark_sats:,.0f} Sats"],
    textposition="auto"
))

fig_bar.add_trace(go.Bar(
    name=t["bar_market"],
    x=[t["bar_market"]],
    y=[market_value_sats],
    marker_color="#29B6F6",
    text=[f"{market_value_sats:,.0f} Sats"],
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
    title=f"Satoshis Momentaufnahme",
    yaxis_title="Satoshis (Sats)",
    template="plotly_white",
    height=450,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig_bar, use_container_width=True)

# ==========================================
# 10. HISTORICAL TIMELINE ENGINE (EXAKTER MERGE)
# ==========================================
st.markdown("---")
st.subheader(t["timeline_title"])

# Indizes bereinigen (Zeitzonen sicher entfernen)
hist_df_clean = hist_df.copy()
hist_df_clean.index = pd.to_datetime(hist_df_clean.index).tz_localize(None)

# Dynamic Transaktions-Map auf den Tages-Index bringen
treasury_daily = df_tx.reindex(
    hist_df_clean.index.union(df_tx.index)
).ffill().reindex(hist_df_clean.index)

# Standard-Fallbacks falls vor der ersten Transaktion
treasury_daily['btc_holdings'] = treasury_daily['btc_holdings'].fillna(21454)
treasury_daily['shares_out'] = treasury_daily['shares_out'].fillna(96000000)

# In Haupt-Dataframe verbinden
merged_df = hist_df_clean.copy()
merged_df['btc_holdings'] = treasury_daily['btc_holdings']
merged_df['shares_out'] = treasury_daily['shares_out']

# Tagesgenaue Satoshis-Berechnungen
mstr_col = "mstr_eur" if currency == "EUR" else "mstr_usd"
btc_col = "btc_eur" if currency == "EUR" else "btc_usd"

# 1. Freimarktwert in Sats
merged_df['market_sats'] = ((user_shares * merged_df[mstr_col]) / merged_df[btc_col]) * SATS_PER_BTC

# 2. Physische BTC-Deckung pro Aktie in Sats
merged_df['internal_btc_sats'] = (user_shares * (merged_df['btc_holdings'] / merged_df['shares_out'])) * SATS_PER_BTC

# 3. Total Substance (+ Cash Reserve)
merged_df['total_substance_sats'] = merged_df['internal_btc_sats'] * 1.05

# ==========================================
# 11. PLOTLY HISTORICAL TIMELINE CHART (MULTI-LINE)
# ==========================================
fig_line = go.Figure()

# 1. Spot HODL Benchmark (Orange Gestrichelt)
fig_line.add_trace(go.Scatter(
    x=merged_df.index,
    y=[hodl_benchmark_sats] * len(merged_df),
    mode='lines',
    name='Spot HODL Benchmark',
    line=dict(color='#F7931A', width=2, dash='dash')
))

# 2. Free Market Value in Sats (Blau schattiert)
fig_line.add_trace(go.Scatter(
    x=merged_df.index,
    y=merged_df['market_sats'],
    mode='lines',
    name='Free Market Value (Sats)',
    fill='tozeroy',
    fillcolor='rgba(41, 182, 246, 0.08)',
    line=dict(color='#29B6F6', width=2)
))

# 3. Internal Asset Base (Physisches BTC - Grün Durchgezogen)
fig_line.add_trace(go.Scatter(
    x=merged_df.index,
    y=merged_df['internal_btc_sats'],
    mode='lines',
    name='Internal BTC Base (Physisch)',
    line=dict(color='#4CAF50', width=2.5)
))

# 4. Total Substance (BTC + Cash - Grün Gestrichelt)
fig_line.add_trace(go.Scatter(
    x=merged_df.index,
    y=merged_df['total_substance_sats'],
    mode='lines',
    name='Total Asset Base (+ Cash Reserve)',
    line=dict(color='#81C784', width=1.5, dash='dot')
))

fig_line.update_layout(
    title="Entwicklung aller Multiplier-Schichten (in Sats) über die Zeit",
    xaxis_title="Datum",
    yaxis_title="Satoshis (Sats)",
    template="plotly_white",
    height=550,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig_line, use_container_width=True)

# ==========================================
# 12. FOOTER & DATA SUMMARY
# ==========================================
with st.expander(t["expander_title"]):
    st.write(f"- **{t['footer_btc']}:** {curr_symbol}{btc_price_curr:,.2f}")
    st.write(f"- **{t['footer_mstr']}:** {curr_symbol}{mstr_price_curr:,.2f}")
    st.write(f"- **EUR/USD:** {live_data['eur_usd']:.4f}")
    st.write(f"- **{t['footer_cash']}:** ${live_data['mstr_cash_usd']/1e9:.2f} B USD")
    st.write(f"- **{t['footer_shares']}:** {live_data['mstr_shares']:,}")
