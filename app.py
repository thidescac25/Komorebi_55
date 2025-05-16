import streamlit as st
import pandas as pd
import sys
import os
import plotly.graph_objects as go
import numpy as np

# Ajouter src/ au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from data_loader import (
    load_portfolio_data, 
    get_stock_data, 
    load_sector_country_data
)
from stock_utils import get_currency_mapping, get_dividend_yields
from ui_components import (
    apply_custom_css,
    create_scrolling_ticker,
    create_title,
    determine_currency,
    create_footer
)
from visualization import create_stock_chart

# ─── Config de la page ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Komorebi Investments 55 – Présentation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

apply_custom_css()

# ─── Titre principal ─────────────────────────────────────────────────────────
st.markdown(create_title("Komorebi Investments 55 – Présentation <span style='font-size:0.6em;'>(page 1/2)</span>"), unsafe_allow_html=True)

# ─── Chargement des données ───────────────────────────────────────────────────
portfolio_df = load_portfolio_data()
currency_mapping = get_currency_mapping()
dividend_yields   = get_dividend_yields()

@st.cache_data(ttl=60)
def get_all_stock_data(tickers):
    d = {}
    for t in tickers:
        d[t] = get_stock_data(t)
    return d

tickers = portfolio_df["Ticker"].tolist()
stock_data_dict = get_all_stock_data(tickers)

# Charger secteur/pays pour la table
df_sc = load_sector_country_data(tickers)
sector_map  = dict(zip(df_sc["Ticker"], df_sc["Sector"]))
country_map = dict(zip(df_sc["Ticker"], df_sc["Country"]))

# ─── Bandeau défilant ─────────────────────────────────────────────────────────
st.markdown(
    create_scrolling_ticker(portfolio_df, stock_data_dict, currency_mapping),
    unsafe_allow_html=True
)

# ─── Sélecteur de société ────────────────────────────────────────────────────
st.markdown('<div class="select-label">Sélectionnez une société</div>', unsafe_allow_html=True)
company = st.selectbox("", portfolio_df["Société"].tolist(), label_visibility="collapsed")

row = portfolio_df[portfolio_df["Société"] == company].iloc[0]
ticker = row["Ticker"]
stock_data = get_stock_data(ticker, detailed=True)
currency   = determine_currency(ticker)

# ─── En-tête société ─────────────────────────────────────────────────────────
st.markdown(f"""
<div class="company-header">{company}</div>
<div class="sector-header">{stock_data['industry']} – {stock_data['country']}</div>
""", unsafe_allow_html=True)

# ─── Business Model ─────────────────────────────────────────────────────────
st.markdown('<div class="section-container">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Business Model de la société</div>', unsafe_allow_html=True)
st.markdown(f'<div class="business-text">{row["Business_models"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ─── Statistiques du jour ───────────────────────────────────────────────────
st.markdown('<div class="section-container" style="padding-top:0;">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Statistiques du jour</div>', unsafe_allow_html=True)

cols = st.columns(5)
metrics = [
    ("Valorisation",   stock_data["pe_ratio"],        "PER",        False),
    ("Rendement",      stock_data["dividend_yield"],  "Dividende",  True),
    ("Performance",    stock_data["ytd_change"],      "YTD",        True),
    ("BPA",            stock_data["eps"],             "Par action", False),
    ("Capitalisation", stock_data["market_cap"],      "Milliards",  False),
]
beige = "#f9f5f2"

for col, (title, val, subtitle, is_pct) in zip(cols, metrics):
    color = "#28a745" if is_pct and val >= 0 else "#dc3545" if is_pct else "#102040"
    disp  = f"{val:+.2f}%" if is_pct else f"{val:.2f}"
    with col:
        st.markdown(f"""
        <div style="background:{beige}; padding:20px; border-radius:10px; text-align:center;">
          <div style="font-size:14px; color:#693112; margin-bottom:10px;">{title}</div>
          <div style="font-size:28px; font-weight:bold; color:{color};">{disp}</div>
          <div style="font-size:14px; color:#888;">{subtitle}</div>
        </div>
        """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ─── Performance sur 52 semaines ─────────────────────────────────────────────
st.markdown('<div class="section-container">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Performance sur 52 semaines</div>', unsafe_allow_html=True)

hist = stock_data.get("history", pd.DataFrame())
if not hist.empty:
    sel, *_ = st.radio("Période", ["1 mois","6 mois","1 an"], horizontal=True, index=2)
    fig, *_ = create_stock_chart(hist, ticker, currency, sel)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Données historiques non disponibles pour cette action.")
st.markdown('</div>', unsafe_allow_html=True)

# ─── Composition du portefeuille ───────────────────────────────────────────────
st.markdown('<div class="section-title">Composition du portefeuille</div>', unsafe_allow_html=True)

# Préparation du DataFrame
comp = []
for _, r in portfolio_df.iterrows():
    sd = stock_data_dict.get(r["Ticker"], {})
    comp.append({
        "Société":               r["Société"],
        "Variation (%) du jour": sd.get("percent_change", 0),
        "Prix":                  sd.get("current_price", 0),
        "Devise":                determine_currency(r["Ticker"]),
        "Secteur":               sector_map.get(r["Ticker"], "N/A"),
        "Pays":                  country_map.get(r["Ticker"], "N/A"),
    })
comp_df = pd.DataFrame(comp)
comp_df.index = range(1, len(comp_df) + 1)

# Fonction pour déterminer la couleur du fond en fonction de la variation
def get_bg_color(val):
    if val > 0:
        return "#9CAF88"  # Vert olive clair pour les valeurs positives
    elif val < 0:
        return "#C8AD7F"  # Beige ambré pour les valeurs négatives
    else:
        return "#DBDBCE"  # Beige grisé clair pour les valeurs neutres

# Créer des valeurs pour les cellules formatées avec texte en gras
index_vals = [f"<b>{i}</b>" for i in range(1, len(comp_df) + 1)]
society_vals = [f"<b>{val}</b>" for val in comp_df['Société']]
price_vals = [f"<b>{val:.2f}</b>" for val in comp_df['Prix']]
device_vals = [f"<b>{val}</b>" for val in comp_df['Devise']]
sector_vals = [f"<b>{val}</b>" for val in comp_df['Secteur']]
country_vals = [f"<b>{val}</b>" for val in comp_df['Pays']]

# Préparer les valeurs de variation formatées et les couleurs de fond
variation_vals = []
bg_colors = []

for val in comp_df["Variation (%) du jour"]:
    if val > 0:
        variation_vals.append(f"<b>+{val:.2f}%</b>")
    else:
        variation_vals.append(f"<b>{val:.2f}%</b>")
    bg_colors.append(get_bg_color(val))

# Créer le tableau avec l'ordre des colonnes modifié et le gradient de couleur pour la variation
fig = go.Figure()

# Ajouter le tableau principal avec le nouvel ordre des colonnes
fig.add_trace(go.Table(
    columnwidth=[40, 200, 120, 80, 60, 150, 120],  # Élargir la colonne Société
    header=dict(
        values=[
            '<b>Index</b>', 
            '<b>Société</b>',
            '<b>Variation du jour (%)</b>',
            '<b>Prix</b>',
            '<b>Devise</b>', 
            '<b>Secteur</b>', 
            '<b>Pays</b>'
        ],
        font=dict(size=14, color='white'),
        fill_color='#693112',  # Marron foncé pour les en-têtes
        align=['center', 'center', 'center', 'center', 'center', 'center', 'center'],
        height=40
    ),
    cells=dict(
        values=[
            index_vals, 
            society_vals,
            variation_vals,
            price_vals,
            device_vals,
            sector_vals,
            country_vals
        ],
        font=dict(size=13, color='#102040', family="Arial"),  # Texte en bleu foncé et en gras
        fill_color=[
            'white', 
            'white',
            bg_colors,  # Appliquer les couleurs de fond pour la colonne variation
            'white',
            'white', 
            'white', 
            'white'
        ],
        align=['center', 'left', 'center', 'center', 'center', 'center', 'center'],
        line_color='lightgrey',  # Légère bordure entre les cellules
        height=30
    )
))

# Ajuster la mise en page
fig.update_layout(
    margin=dict(l=5, r=5, t=5, b=5),
    height=400
)

# Afficher le tableau Plotly
st.plotly_chart(fig, use_container_width=True)

# ─── Espacement avant métriques globales ──────────────────────────────────────
st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)

# ─── Performance du jour des valeurs ───────────────────────────────────────────
st.markdown('<div class="section-title">Performance du jour des valeurs</div>', unsafe_allow_html=True)

n     = len(comp_df)
pos   = sum(v>0 for v in comp_df["Variation (%) du jour"])
neg   = sum(v<0 for v in comp_df["Variation (%) du jour"])
neu   = n - pos - neg
pos_p = pos/n*100; neg_p = neg/n*100; neu_p = neu/n*100

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
      <div class="metric-container">
        <div class="metric-title">📈 Nombre de valeurs</div>
        <div class="metric-value">{n}</div>
        <div class="metric-subtitle">actions</div>
      </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
      <div class="metric-container">
        <div class="metric-title">💹 Performances positives</div>
        <div class="metric-value positive">{pos} ({pos_p:.1f}%)</div>
        <div class="metric-subtitle">valeurs en hausse</div>
      </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown(f"""
      <div class="metric-container">
        <div class="metric-title">📉 Performances négatives</div>
        <div class="metric-value negative">{neg} ({neg_p:.1f}%)</div>
        <div class="metric-subtitle">valeurs en baisse</div>
      </div>
    """, unsafe_allow_html=True)
with c4:
    st.markdown(f"""
      <div class="metric-container">
        <div class="metric-title">⚖️ Performances neutres</div>
        <div class="metric-value neutral">{neu} ({neu_p:.1f}%)</div>
        <div class="metric-subtitle">valeurs stables</div>
      </div>
    """, unsafe_allow_html=True)

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown(create_footer(), unsafe_allow_html=True)