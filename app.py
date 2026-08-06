import streamlit as st
import plotly.graph_objects as go
import yfinance as yf

# ==========================================
# 1. STREAMLIT PAGE CONFIG & STYLING
# ==========================================
st.set_page_config(
    page_title="MSTR Satoshi Multiplier Dashboard",
    page_icon="₿",
    layout="wide"
)

st.title("₿ Satoshi Multiplier Dashboard ($MSTR)")
st.caption("Visualisierung des internen Bitcoin-Substanzgewinns von MicroStrategy vs. Spot HODL Benchmark")

# ==========================================
# 2. DATA FETCHING (LIVE & FALLBACKS)
# ==========================================
@st.cache_data(ttl=3600)  # Daten für 1 Std. cachen
def fetch_live_data():
    """
    Holt Live-Daten via Yahoo Finance.
    Nutzt Fallback-Werte gemäß Prompt-Definition, falls APIs fehlschlagen.
    """
    # Standard Fallbacks laut Auftrag
    defaults = {
        "btc_usd": 65000.0,
        "mstr_usd": 135.0,
        "eur_usd": 1.08,
        "mstr_shares": 353_900_000,
        "mstr_btc": 842_138,
        "mstr_cash_usd": 4_000_000_000
    }
    
    try:
        # Ticker laden
        btc_ticker = yf.Ticker("BTC-USD")
        mstr_ticker = yf.Ticker("MSTR")
        eur_ticker = yf.Ticker("EURUSD=X")
        
        # Preise abfragen
        btc_usd = btc_ticker.history(period="1d")['Close'].iloc[-1]
        mstr_usd = mstr_ticker.history(period="1d")['Close'].iloc[-1]
        eur_usd = eur_ticker.history(period="1d")['Close'].iloc[-1]
        
        return {
            "btc_usd": float(btc_usd),
            "mstr_usd": float(mstr_usd),
            "eur_usd": float(eur_usd),
            "mstr_shares": defaults["mstr_shares"],
            "mstr_btc": defaults["mstr_btc"],
            "mstr_cash_usd": defaults["mstr_cash_usd"]
        }
    except Exception:
        # Bei Fehler Fallback verwenden
        return defaults

live_data = fetch_live_data()

# Umrechnung der Live-Preise in EUR
btc_price_curr_usd = live_data["btc_usd"]
mstr_price_curr_usd = live_data["mstr_usd"]
eur_usd_curr = live_data["eur_usd"]

btc_price_curr_eur = btc_price_curr_usd / eur_usd_curr
mstr_price_curr_eur = mstr_price_curr_usd / eur_usd_curr

# ==========================================
# 3. USER INPUTS (SIDEBAR)
# ==========================================
st.sidebar.header("🛠️ Deine Kaufdaten & Parameter")

user_shares = st.sidebar.number_input(
    "Anzahl MSTR Aktien (User_Shares)", 
    min_value=1, value=100, step=1
)

user_cost_basis_eur = st.sidebar.number_input(
    "Kaufpreis pro Aktie in EUR (User_Cost_Basis_EUR)", 
    min_value=0.01, value=57.92, step=1.0
)

btc_price_past_eur = st.sidebar.number_input(
    "BTC Kurs bei Kauf in EUR (BTC_Price_Past)", 
    min_value=1.0, value=38800.0, step=500.0
)

st.sidebar.markdown("---")
st.sidebar.subheader("🎛️ Markt-Simulation")

simulated_premium = st.sidebar.slider(
    "Simuliertes NAV-Aufgeld/Rabatt (Simulated_Premium %)",
    min_value=-20, max_value=50, value=0, step=1,
    help="Skaliert den aktuellen Freimarkt-Wert um eine Auf-/Abschlags-Prämie."
)

# Premium auf den Marktpreis anwenden
premium_factor = 1.0 + (simulated_premium / 100.0)
mstr_price_simulated_eur = mstr_price_curr_eur * premium_factor

# ==========================================
# 4. MATHEMATICAL ENGINE (Sats-Logic)
# ==========================================
# Constant: 1 BTC = 100,000,000 Satoshis
SATS_PER_BTC = 100_000_000

# Step 1: Historical Benchmark (Input Capital)
total_invest_eur = user_shares * user_cost_basis_eur
hodl_benchmark_sats = (total_invest_eur / btc_price_past_eur) * SATS_PER_BTC

# Step 2: Free Market Today (Liquidation Value with Simulated Premium)
market_value_eur = user_shares * mstr_price_simulated_eur
market_value_sats = (market_value_eur / btc_price_curr_eur) * SATS_PER_BTC

# Step 3: Saylor Engine (Internal BTC Value)
current_btc_per_share = live_data["mstr_btc"] / live_data["mstr_shares"]
internal_btc_sats = user_shares * current_btc_per_share * SATS_PER_BTC

# Step 4: Dry Powder (Cash-to-Sats)
cash_per_share_usd = live_data["mstr_cash_usd"] / live_data["mstr_shares"]
total_user_cash_usd = user_shares * cash_per_share_usd
internal_cash_sats = (total_user_cash_usd / btc_price_curr_usd) * SATS_PER_BTC

# Step 5: Total Corporate Substance
total_substance_sats = internal_btc_sats + internal_cash_sats

# Percentages / Renditen berechnen
fiat_return_pct = ((market_value_eur - total_invest_eur) / total_invest_eur) * 100
market_sats_yield_pct = ((market_value_sats - hodl_benchmark_sats) / hodl_benchmark_sats) * 100
substance_yield_pct = ((total_substance_sats - hodl_benchmark_sats) / hodl_benchmark_sats) * 100

# ==========================================
# 5. UI: MAIN METRIC CARDS
# ==========================================
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="EUR Return (Fiat Yield)",
        value=f"€{market_value_eur:,.2f}",
        delta=f"{fiat_return_pct:+.2f}% (Invest: €{total_invest_eur:,.2f})"
    )

with col2:
    st.metric(
        label="Market Sats Yield (Open Market)",
        value=f"{market_value_sats:,.0f} Sats",
        delta=f"{market_sats_yield_pct:+.2f}% vs. Spot HODL"
    )

with col3:
    st.metric(
        label="Corporate Substance Yield (Internal)",
        value=f"{total_substance_sats:,.0f} Sats",
        delta=f"{substance_yield_pct:+.2f}% vs. Spot HODL"
    )

st.markdown("---")

# ==========================================
# 6. VISUALIZATION: STACKED BAR CHART
# ==========================================
st.subheader("📊 Der Satoshi-Multiplier im Vergleich")

fig = go.Figure()

# Bar 1: Spot HODL Benchmark
fig.add_trace(go.Bar(
    name="Spot HODL Benchmark",
    x=["1. Spot HODL Benchmark"],
    y=[hodl_benchmark_sats],
    marker_color="#F7931A", # Bitcoin Orange
    text=[f"{hodl_benchmark_sats:,.0f} Sats"],
    textposition="auto"
))

# Bar 2: Free Market Value
fig.add_trace(go.Bar(
    name="Free Market Value (Market Sats)",
    x=["2. Free Market Value"],
    y=[market_value_sats],
    marker_color="#29B6F6", # Light Blue
    text=[f"{market_value_sats:,.0f} Sats"],
    textposition="auto"
))

# Bar 3: Stacked Internal Asset Base (Layer 1: BTC)
fig.add_trace(go.Bar(
    name="Physical BTC Backing",
    x=["3. Internal Asset Base"],
    y=[internal_btc_sats],
    marker_color="#4CAF50", # Green
    text=[f"{internal_btc_sats:,.0f} Sats"],
    textposition="inside"
))

# Bar 3: Stacked Internal Asset Base (Layer 2: Cash)
fig.add_trace(go.Bar(
    name="Corporate Cash Reserve in Sats",
    x=["3. Internal Asset Base"],
    y=[internal_cash_sats],
    marker_color="#81C784", # Light Green
    text=[f"{internal_cash_sats:,.0f} Sats"],
    textposition="inside"
))

# Layout Styling
fig.update_layout(
    barmode="stack",
    title="Anzahl Satoshis: HODL vs. Marktwert vs. Physische Firmen-Substanz",
    yaxis_title="Satoshis (Sats)",
    template="plotly_white",
    height=550,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 7. FOOTER & DATA SUMMARY
# ==========================================
with st.expander("ℹ️ Aktuelle Markt- und Fundamentaldaten anzeigen"):
    st.write(f"- **BTC Preis (USD):** ${btc_price_curr_usd:,.2f}")
    st.write(f"- **MSTR Preis (USD):** ${mstr_price_curr_usd:,.2f}")
    st.write(f"- **EUR/USD Kurs:** {eur_usd_curr:.4f}")
    st.write(f"- **MSTR BTC-Bestand:** {live_data['mstr_btc']:,} BTC")
    st.write(f"- **MSTR Aktien im Umlauf:** {live_data['mstr_shares']:,}")
