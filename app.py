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
# 2. LANGUAGE & CURRENCY TRANSLATIONS
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
        "timeline_title": "📈 Satoshi Multiplier Zeitverlauf",
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
        "timeline_title": "📈 Satoshi Multiplier Historical Performance",
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
# 3. SIDEBAR: CURRENCY & LANGUAGE SELECTOR
# ==========================================
st.sidebar.header("🌐 Language / Währung")
currency = st.sidebar.radio(
    "Select Currency / Währung wählen",
    options=["EUR", "USD"],
    index=0
)

lang = "DE" if currency == "EUR" else "EN"
t = TRANSLATIONS[lang]
curr_symbol = "€" if currency == "EUR" else "$"

st.title(t["title"])
st.caption(t["subtitle"])

# ==========================================
# 4. DATA FETCHING (LIVE & HISTORICAL)
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
    """Holt die tägliche Preis-Historie ab dem Kaufdatum (robust gegen Börsen-Lücken & Wochenenden)."""
    start_str = start_date.strftime('%Y-%m-%d')
    
    try:
        mstr_df = yf.Ticker("MSTR").history(start=start_str)['Close']
        btc_df = yf.Ticker("BTC-USD").history(start=start_str)['Close']
        eur_df = yf.Ticker("EURUSD=X").history(start=start_str)['Close']

        # Auf gemeinsamem Datum zusammenführen
        df = pd.DataFrame({
            "mstr_usd": mstr_df,
            "btc_usd": btc_df,
            "eur_usd": eur_df
        })

        # Vorwärts/Rückwärts ausfüllen gegen Lücken an Wochenenden/Feiertagen
        df = df.ffill().bfill().dropna()

        if df.empty:
            raise ValueError("Keine Daten vorhanden.")

        df['mstr_eur'] = df['mstr_usd'] / df['eur_usd']
        df['btc_eur'] = df['btc_usd'] / df['eur_usd']

        return df

    except Exception:
        # Fallback falls API ausfällt
        dates = pd.date_range(start=start_date, periods=2)
        return pd.DataFrame({
            "mstr_usd": [135.0, 135.0],
            "btc_usd": [65000.0, 65000.0],
            "eur_usd": [1.08, 1.08],
            "mstr_eur": [125.0, 125.0],
            "btc_eur": [60000.0, 60000.0]
        }, index=dates)

live_data = fetch_live_data()

# Aktuelle Preise in gewählter Währung
if currency == "EUR":
    btc_price_curr = live_data["btc_usd"] / live_data["eur_usd"]
    mstr_price_curr = live_data["mstr_usd"] / live_data["eur_usd"]
else:
    btc_price_curr = live_data["btc_usd"]
    mstr_price_curr = live_data["mstr_usd"]

# ==========================================
# 5. USER INPUTS (SIDEBAR)
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
    min_value=1, value=100, step=1
)

# Laden der historischen Daten
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
    mstr_price_past = 57.92 if currency == "EUR" else 63.00
    btc_price_past = 38800.0 if currency == "EUR" else 42000.0

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
# 6. MATHEMATICAL ENGINE
# ==========================================
SATS_PER_BTC = 100_000_000

total_invest = user_shares * mstr_price_past

# Step 1: Historical HODL Benchmark
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
# 7. UI DISPLAY (KPI CARDS)
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
# 8. PLOTLY SNAPSHOT CHART (BAR)
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
# 9. PLOTLY HISTORICAL TIMELINE CHART (LINE)
# ==========================================
st.markdown("---")
st.subheader(t["timeline_title"])

# Tagesgenaue Satoshis-Berechnung
mstr_col = "mstr_eur" if currency == "EUR" else "mstr_usd"
btc_col = "btc_eur" if currency == "EUR" else "btc_usd"

hist_df['market_sats'] = ( (user_shares * hist_df[mstr_col]) / hist_df[btc_col] ) * SATS_PER_BTC

fig_line = go.Figure()

fig_line.add_trace(go.Scatter(
    x=hist_df.index,
    y=[hodl_benchmark_sats] * len(hist_df),
    mode='lines',
    name='Spot HODL Benchmark',
    line=dict(color='#F7931A', width=2, dash='dash')
))

fig_line.add_trace(go.Scatter(
    x=hist_df.index,
    y=hist_df['market_sats'],
    mode='lines',
    name='Market Sats (Freier Markt)',
    fill='tozeroy',
    fillcolor='rgba(41, 182, 246, 0.1)',
    line=dict(color='#29B6F6', width=2.5)
))

fig_line.update_layout(
    title="Entwicklung des Freimarktwerts (in Sats) vs. Spot HODL Benchmark",
    xaxis_title="Datum",
    yaxis_title="Satoshis (Sats)",
    template="plotly_white",
    height=500,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig_line, use_container_width=True)

# ==========================================
# 10. FOOTER & DATA SUMMARY
# ==========================================
with st.expander(t["expander_title"]):
    st.write(f"- **{t['footer_btc']}:** {curr_symbol}{btc_price_curr:,.2f}")
    st.write(f"- **{t['footer_mstr']}:** {curr_symbol}{mstr_price_curr:,.2f}")
    st.write(f"- **EUR/USD:** {live_data['eur_usd']:.4f}")
    st.write(f"- **{t['footer_cash']}:** ${live_data['mstr_cash_usd']/1e9:.2f} B USD")
    st.write(f"- **{t['footer_shares']}:** {live_data['mstr_shares']:,}")        "bar_market": "2. Free Market Value",
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
        "timeline_title": "📈 Satoshi Multiplier Historical Performance",
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
# 3. SIDEBAR: CURRENCY & LANGUAGE SELECTOR
# ==========================================
st.sidebar.header("🌐 Language / Währung")
currency = st.sidebar.radio(
    "Select Currency / Währung wählen",
    options=["EUR", "USD"],
    index=0
)

lang = "DE" if currency == "EUR" else "EN"
t = TRANSLATIONS[lang]
curr_symbol = "€" if currency == "EUR" else "$"

st.title(t["title"])
st.caption(t["subtitle"])

# ==========================================
# 4. DATA FETCHING (LIVE & HISTORICAL)
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
    """Holt die tägliche Preis-Historie ab dem Kaufdatum für MSTR und BTC."""
    start_str = start_date.strftime('%Y-%m-%d')
    
    mstr_df = yf.Ticker("MSTR").history(start=start_str)['Close']
    btc_df = yf.Ticker("BTC-USD").history(start=start_str)['Close']
    eur_df = yf.Ticker("EURUSD=X").history(start=start_str)['Close']

    df = pd.DataFrame({
        "mstr_usd": mstr_df,
        "btc_usd": btc_df,
        "eur_usd": eur_df
    }).dropna()

    df['mstr_eur'] = df['mstr_usd'] / df['eur_usd']
    df['btc_eur'] = df['btc_usd'] / df['eur_usd']

    return df

live_data = fetch_live_data()

# Aktuelle Preise
if currency == "EUR":
    btc_price_curr = live_data["btc_usd"] / live_data["eur_usd"]
    mstr_price_curr = live_data["mstr_usd"] / live_data["eur_usd"]
else:
    btc_price_curr = live_data["btc_usd"]
    mstr_price_curr = live_data["mstr_usd"]

# ==========================================
# 5. USER INPUTS (SIDEBAR)
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
    min_value=1, value=100, step=1
)

# Laden der Zeitreihe
hist_df = fetch_historical_series(purchase_date)

# Kaufkurse ermitteln
if currency == "EUR":
    mstr_price_past = hist_df['mstr_eur'].iloc[0]
    btc_price_past = hist_df['btc_eur'].iloc[0]
else:
    mstr_price_past = hist_df['mstr_usd'].iloc[0]
    btc_price_past = hist_df['btc_usd'].iloc[0]

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
# 6. MATHEMATICAL ENGINE
# ==========================================
SATS_PER_BTC = 100_000_000

total_invest = user_shares * mstr_price_past

# Step 1: Historical HODL Benchmark
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

# Percentages
fiat_return_pct = ((market_value_fiat - total_invest) / total_invest) * 100
market_sats_yield_pct = ((market_value_sats - hodl_benchmark_sats) / hodl_benchmark_sats) * 100
substance_yield_pct = ((total_substance_sats - hodl_benchmark_sats) / hodl_benchmark_sats) * 100

# ==========================================
# 7. UI DISPLAY (KPI CARDS)
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
# 8. PLOTLY SNAPSHOT CHART (BAR)
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
# 9. PLOTLY HISTORICAL TIMELINE CHART (LINE)
# ==========================================
st.markdown("---")
st.subheader(t["timeline_title"])

# Tagesgenaue Satoshis-Berechnung für den Freimarkt
mstr_col = "mstr_eur" if currency == "EUR" else "mstr_usd"
btc_col = "btc_eur" if currency == "EUR" else "btc_usd"

hist_df['market_sats'] = ( (user_shares * hist_df[mstr_col]) / hist_df[btc_col] ) * SATS_PER_BTC

fig_line = go.Figure()

# Line 1: HODL Benchmark (konstant)
fig_line.add_trace(go.Scatter(
    x=hist_df.index,
    y=[hodl_benchmark_sats] * len(hist_df),
    mode='lines',
    name='Spot HODL Benchmark',
    line=dict(color='#F7931A', width=2, dash='dash')
))

# Line 2: Market Value in Sats über Zeit
fig_line.add_trace(go.Scatter(
    x=hist_df.index,
    y=hist_df['market_sats'],
    mode='lines',
    name='Market Sats (Freier Markt)',
    fill='tozeroy',
    fillcolor='rgba(41, 182, 246, 0.1)',
    line=dict(color='#29B6F6', width=2.5)
))

fig_line.update_layout(
    title="Entwicklung des Freimarktwerts (in Sats) vs. Spot HODL Benchmark",
    xaxis_title="Datum",
    yaxis_title="Satoshis (Sats)",
    template="plotly_white",
    height=500,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig_line, use_container_width=True)

# ==========================================
# 10. FOOTER & DATA SUMMARY
# ==========================================
with st.expander(t["expander_title"]):
    st.write(f"- **{t['footer_btc']}:** {curr_symbol}{btc_price_curr:,.2f}")
    st.write(f"- **{t['footer_mstr']}:** {curr_symbol}{mstr_price_curr:,.2f}")
    st.write(f"- **EUR/USD:** {live_data['eur_usd']:.4f}")
    st.write(f"- **{t['footer_cash']}:** ${live_data['mstr_cash_usd']/1e9:.2f} B USD")
    st.write(f"- **{t['footer_shares']}:** {live_data['mstr_shares']:,}")
