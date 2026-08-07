import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf

# ==============================================================================
# CONFIG & TRANSLATIONS
# ==============================================================================
st.set_page_config(page_title="Saylor Engine", page_icon="⚡", layout="wide")

TRANSLATIONS = {
    "DE": {
        "title": "⚡ Saylor Engine — Financial Analytics",
        "sidebar_header": "Einstellungen",
        "lang_select": "Sprache auswählen",
        "chart_title": "Marktwert vs. HODL Benchmark",
        "timeline_title": "Verlauf: Satoshis pro Aktie over Time",
        "yaxis_sats": "Satoshis pro Aktie (Sats / Share)",
        "volume_title": "MSTR Handelsvolumen vs. Ausstehende Aktien",
        "vol_axis": "Handelsvolumen (Stück)",
        "shares_axis": "Ausstehende Aktien (Shares Outstanding)",
        "bar_market": "Marktwert (Sats)",
        "bar_hodl": "HODL Benchmark (Sats)",
    },
    "EN": {
        "title": "⚡ Saylor Engine — Financial Analytics",
        "sidebar_header": "Settings",
        "lang_select": "Select Language",
        "chart_title": "Market Value vs. HODL Benchmark",
        "timeline_title": "Timeline: Satoshis per Share over Time",
        "yaxis_sats": "Satoshis per Share (Sats / Share)",
        "volume_title": "MSTR Trading Volume vs. Shares Outstanding",
        "vol_axis": "Trading Volume (Shares)",
        "shares_axis": "Shares Outstanding",
        "bar_market": "Market Value (Sats)",
        "bar_hodl": "HODL Benchmark (Sats)",
    }
}

# Sprachauswahl
lang = st.sidebar.selectbox("Language / Sprache", ["DE", "EN"])
t = TRANSLATIONS[lang]

st.title(t["title"])

# ==============================================================================
# DATA LOADING (YFINANCE)
# ==============================================================================
@st.cache_data(ttl=3600)
def load_mstr_volume_and_shares():
    ticker = yf.Ticker("MSTR")
    try:
        hist = ticker.history(period="2y")
        shares = ticker.get_shares_full(start=hist.index[0].strftime("%Y-%m-%d"))
    except Exception as e:
        st.error(f"Fehler beim Laden der yfinance Daten: {e}")
        hist, shares = pd.DataFrame(), None
    return hist, shares

mstr_hist, mstr_shares = load_mstr_volume_and_shares()

# ==============================================================================
# NEUES DIAGRAMM: MSTR HANDELSVOLUMEN & SHARES ISSUED
# ==============================================================================
st.markdown("---")
st.subheader(f"📊 {t['volume_title']}")

if not mstr_hist.empty:
    fig_vol = make_subplots(specs=[[{"secondary_y": True}]])

    # Handelsvolumen (Balken)
    fig_vol.add_trace(
        go.Bar(
            x=mstr_hist.index,
            y=mstr_hist["Volume"],
            name=t["vol_axis"],
            marker_color="rgba(41, 182, 246, 0.4)",
        ),
        secondary_y=False,
    )

    # Shares Outstanding (Linie)
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

    fig_vol.update_layout(
        title=dict(text=t["volume_title"], font=dict(size=18)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(128,128,128,0.9)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis=dict(gridcolor="rgba(128, 128, 128, 0.2)"),
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
else:
    st.warning("Keine Marktdaten von yfinance verfügbar.")
