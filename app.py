import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
from datetime import date, datetime, timedelta

# ==========================================
# 1. STREAMLIT PAGE CONFIG & STYLING
# ==========================================
st.set_page_config(
    page_title="Saylor Engine Dashboard",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Saylor Engine ($MSTR)")
st.caption("Automatisches Satoshi-Multiplier & Substanz-Dashboard")

# ==========================================
# 2. DATA FETCHING (LIVE & HISTORICAL)
# ==========================================
@st.cache_data(ttl=3600)
def fetch_live_data():
    """Holt aktuelle Live-Preise."""
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
def fetch_historical_prices(target_date):
    """
    Holt die historischen Schlusskurse für MSTR und BTC (in EUR) 
    für ein bestimmtes Datum.
    """
    start_str = target_date.strftime('%Y-%m-%d')
    end_date = target_date + timedelta(days=5) # Puffert Wochenenden ab
    end_str = end_date.strftime('%Y-%m-%d')

    try:
        # Historische Kurse abrufen
        mstr_hist = yf.Ticker("MSTR").history(start=start_str, end=end_str)
        btc_hist = yf.Ticker("BTC-EUR").history(start=start_str, end=end_str)
        
        # Falls BTC-EUR nicht direkt greift:
        if btc_hist.empty:
            btc_usd_hist = yf.Ticker("BTC-USD").history(start=start_str, end=end_str)
            eur_usd_hist = yf.Ticker("EURUSD=X").history(start=start_str, end=end_str)
            btc_price = btc_usd_hist['Close'].iloc[0] / eur_usd_hist['Close'].iloc[0]
        else:
            btc_price = btc_hist['Close'].iloc[0]

        mstr_price_usd = mstr_hist['Close'].iloc[0]
        
        # Wechselkurs am Tag des Kaufs
        eur_usd_hist = yf.Ticker("EURUSD=X").history(start=start_str, end=end_str)
        eur_rate = eur_usd_hist['Close'].iloc[0] if not eur_usd_hist.empty else 1.08
        
        mstr_price_eur = mstr_price_usd / eur_rate

        return float(mstr_price_eur), float(btc_price)
    except Exception:
        # Fallback auf Standardwerte falls Datum fehlschlägt (z.B. Feiertage/Zukunft)
        return 57.92, 38800.0

live_data = fetch_live_data()

# Umrechnung aktuelle Preise in EUR
btc_price_curr_eur = live_data["btc_usd"] / live_data["eur_usd"]
mstr_price_curr_eur = live_data["mstr_usd"] / live_data["eur_usd"]

# ==========================================
# 3. USER INPUTS (EINFACCH & AUTOMATISCH)
# ==========================================
st.sidebar.header("🛒 Deine Kauf-Details")

# 1. Datumswähler
purchase_date = st.sidebar.date_input(
    "Kaufdatum wählen",
    value=date(2024, 1, 15),
    min_value=date(2020, 8, 10), # Seit MSTR die BTC-Strategie fährt
    max_value=date.today()
)

# 2. Aktienanzahl
user_shares = st.sidebar.number_input(
    "Anzahl gekaufter MSTR-Aktien", 
    min_value=1, value=100, step=1
)

# Automatischer Abruf der historischen Kurse
mstr_price_past_eur, btc_price_past_eur = fetch_historical_prices(purchase_date)

# Anzeige der ermittelten historischen Werte in der Sidebar
st.sidebar.markdown("---")
st.sidebar.caption("📌 **Automatisch ermittelte historische Kurse:**")
st.sidebar.text(f"MSTR Kurs am {purchase_date.strftime('%d.%m.%Y')}: €{mstr_price_past_eur:,.2f}")
st.sidebar.text(f"BTC Kurs am {purchase_date.strftime('%d.%m.%Y')}: €{btc_price_past_eur:,.2f}")

st.sidebar.markdown("---")
st.sidebar.subheader("🎛️ Markt-Simulation")

simulated_premium = st.sidebar.slider(
    "Simuliertes NAV-Aufgeld/Rabatt (%)",
    min_value=-20, max_value=50, value=0, step=1
)

premium_factor = 1.0 + (simulated_premium / 100.0)
mstr_price_simulated_eur = mstr_price_curr_eur * premium_factor

# ==========================================
# 4. MATHEMATICAL ENGINE
# ==========================================
SATS_PER_BTC = 100_000_000

# Automatisches Rechnen der Kaufsumme
total_invest_eur = user_shares * mstr_price_past_eur

# Step 1: Historical HODL Benchmark
hodl_benchmark_sats = (total_invest_eur / btc_price_past_eur) * SATS_PER_BTC

# Step 2: Free Market Today
market_value_eur = user_shares * mstr_price_simulated_eur
market_value_sats = (market_value_eur / btc_price_curr_eur) * SATS_PER_BTC

# Step 3: Saylor Engine (Internal BTC)
current_btc_per_share = live_data["mstr_btc"] / live_data["mstr_shares"]
internal_btc_sats = user_shares * current_btc_per_share * SATS_PER_BTC

# Step 4: Dry Powder (Cash)
cash_per_share_usd = live_data["mstr_cash_usd"] / live_data["mstr_shares"]
total_user_cash_usd = user_shares * cash_per_share_usd
internal_cash_sats = (total_user_cash_usd / live_data["btc_usd"]) * SATS_PER_BTC

# Step 5: Total Substance
total_substance_sats = internal_btc_sats + internal_cash_sats

# Renditen
fiat_return_pct = ((market_value_eur - total_invest_eur) / total_invest_eur) * 100
market_sats_yield_pct = ((market_value_sats - hodl_benchmark_sats) / hodl_benchmark_sats) * 100
substance_yield_pct = ((total_substance_sats - hodl_benchmark_sats) / hodl_benchmark_sats) * 100

# ==========================================
# 5. UI DISPLAY
# ==========================================
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="EUR Wertentwicklung (Fiat)",
        value=f"€{market_value_eur:,.2f}",
        delta=f"{fiat_return_pct:+.2f}% (Invest: €{total_invest_eur:,.2f})"
    )

with col2:
    st.metric(
        label="Market Sats Yield (Freier Markt)",
        value=f"{market_value_sats:,.0f} Sats",
        delta=f"{market_sats_yield_pct:+.2f}% vs. Spot HODL"
    )

with col3:
    st.metric(
        label="Substance Yield (Firmen-Substanz)",
        value=f"{total_substance_sats:,.0f} Sats",
        delta=f"{substance_yield_pct:+.2f}% vs. Spot HODL"
    )

st.markdown("---")

# ==========================================
# 6. PLOTLY CHART
# ==========================================
st.subheader("📊 Satoshi Multiplier Vergleich")

fig = go.Figure()

fig.add_trace(go.Bar(
    name="Spot HODL Benchmark",
    x=["1. Spot HODL Benchmark"],
    y=[hodl_benchmark_sats],
    marker_color="#F7931A",
    text=[f"{hodl_benchmark_sats:,.0f} Sats"],
    textposition="auto"
))

fig.add_trace(go.Bar(
    name="Free Market Value (Market Sats)",
    x=["2. Free Market Value"],
    y=[market_value_sats],
    marker_color="#29B6F6",
    text=[f"{market_value_sats:,.0f} Sats"],
    textposition="auto"
))

fig.add_trace(go.Bar(
    name="Physical BTC Backing",
    x=["3. Internal Asset Base"],
    y=[internal_btc_sats],
    marker_color="#4CAF50",
    text=[f"{internal_btc_sats:,.0f} Sats"],
    textposition="inside"
))

fig.add_trace(go.Bar(
    name="Corporate Cash Reserve in Sats",
    x=["3. Internal Asset Base"],
    y=[internal_cash_sats],
    marker_color="#81C784",
    text=[f"{internal_cash_sats:,.0f} Sats"],
    textposition="inside"
))

fig.update_layout(
    barmode="stack",
    title=f"Vergleich der Satoshis (Kaufdatum: {purchase_date.strftime('%d.%m.%Y')})",
    yaxis_title="Satoshis (Sats)",
    template="plotly_white",
    height=550,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)
