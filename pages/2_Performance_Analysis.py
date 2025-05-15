import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime

# Ajouter le dossier src au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importer les modules personnalisés
from src.data_loader import load_portfolio_data, get_stock_data, get_historical_data, load_sector_country_data
from src.stock_utils import get_currency_mapping
from src.ui_components import apply_custom_css, create_scrolling_ticker, create_title, create_footer, create_metric_card
from src.visualization import plot_performance, plot_portfolio_simulation, calculate_portfolio_stats, display_top_contributors

# Configuration de la page
st.set_page_config(
    page_title="Komorebi 55 - Analyse de Performance",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Appliquer le CSS global perso
apply_custom_css()

# CSS pour centrer cellules et en-têtes dans nos tables,
# fixer la largeur du tableau et le centrer
st.markdown(
    """
    <style>
      /* Centre le contenu des cellules */
      .komorebi-table th,
      .komorebi-table td {
        text-align: center !important;
      }
      /* Met le tableau à 90% de la largeur du conteneur, le centre, et fixe le layout */
      .komorebi-table {
        width: 90% !important;
        margin: 0 auto !important;
        table-layout: fixed !important;
      }
    </style>
    """,
    unsafe_allow_html=True
)

# Titre
st.markdown(create_title("Komorebi Investments 55 - Analyse de Performance", "page 3/3"), unsafe_allow_html=True)

# Chargement des données
portfolio_df = load_portfolio_data()
currency_mapping = get_currency_mapping()

@st.cache_data(ttl=60)
def get_all_stock_data(tickers):
    return {t: get_stock_data(t) for t in tickers}

tickers = portfolio_df['Ticker'].tolist()
stock_data_dict = get_all_stock_data(tickers)

# Ticker défilant
st.markdown(create_scrolling_ticker(portfolio_df, stock_data_dict, currency_mapping), unsafe_allow_html=True)

# Présentation performance
st.markdown('<div class="section-title">Présentation de la Performance</div>', unsafe_allow_html=True)
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(
        "<div style='display: flex; align-items: center;'>"
        "<div>Date de début d'investissement</div>"
        "<div style='margin: 0 10px;'> - </div>"
        "<div style='color: #693112; font-style: italic;'>Fixée au 05/01/2023</div>"
        "</div>",
        unsafe_allow_html=True
    )
    start_date = datetime(2023, 1, 5)
with col2:
    indices_options = {
        "CAC 40": "^FCHI",
        "S&P 500": "^GSPC",
        "NASDAQ": "^IXIC",
        "EURO STOXX 50": "^STOXX50E"
    }
    selected = st.multiselect("Indices de référence", options=list(indices_options.keys()), default=["CAC 40"])
    reference_indices = {k: indices_options[k] for k in selected}

end_date = datetime.now()

# Données historiques & graphique
with st.spinner("Chargement des données historiques..."):
    hist_data = get_historical_data(tickers, start_date, end_date)

# <<< Correction : passer reference_indices en argument nommé >>>
perf_fig = plot_performance(
    hist_data,
    reference_indices=reference_indices,
    end_date_ui=end_date,
    force_start_date=start_date
)

if perf_fig:
    st.plotly_chart(perf_fig, use_container_width=True, key="perf")
else:
    st.warning("Pas assez de données pour afficher le graphique de performance.")

# Simulation
st.markdown('<div class="section-title">Simulation d\'investissement</div>', unsafe_allow_html=True)
with st.spinner("Calcul de la simulation..."):
    sim_fig, final_val, gain_loss, pct, _ = plot_portfolio_simulation(
        hist_data, 1_000_000, end_date_ui=end_date, max_traces=15, force_start_date=start_date
    )
if sim_fig:
    st.plotly_chart(sim_fig, use_container_width=True, key="sim")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(create_metric_card("Valeur finale", int(final_val), "Valeur totale du portefeuille", is_currency=True, currency="€"), unsafe_allow_html=True)
    with c2:
        st.markdown(create_metric_card("Gain/Perte", int(gain_loss), "Depuis l'investissement initial", is_currency=True, currency="€", positive_color=True), unsafe_allow_html=True)
    with c3:
        st.markdown(create_metric_card("Performance", pct, "Rendement total", is_percentage=True, positive_color=True), unsafe_allow_html=True)
else:
    st.warning("Pas assez de données pour afficher la simulation.")

# Contributeurs
if hist_data and 'Société' in portfolio_df.columns:
    df_perf = calculate_portfolio_stats(hist_data, portfolio_df, start_date, end_date)
    display_top_contributors(df_perf)
else:
    st.warning("Impossible de calculer les contributeurs à la performance.")

# Analyse par secteur et pays
st.markdown('<div class="section-title">Analyse par Secteur et Pays</div>', unsafe_allow_html=True)
df_sc = load_sector_country_data(tickers)

# Calcul des variations
perf_list = []
for t in tickers:
    if t in hist_data and not hist_data[t].empty:
        dfh = hist_data[t]
        i0 = dfh.index.get_indexer([start_date], method='nearest')[0]
        if 0 <= i0 < len(dfh):
            p0, p1 = dfh['Close'].iloc[i0], dfh['Close'].iloc[-1]
            if p0 > 0:
                pctc = (p1 - p0) / p0 * 100
                comp = portfolio_df[portfolio_df['Ticker'] == t]
                name = comp.iloc[0]['Société'] if not comp.empty else t
                perf_list.append({'Ticker': t, 'Société': name, 'Variation(%)': pctc})
perf_df = pd.DataFrame(perf_list)
analysis_df = pd.merge(df_sc, perf_df, on='Ticker')

# --- Performances par secteur ---
st.markdown("### Performances par secteur")
sector_stats = (
    analysis_df.groupby('Sector')
    .agg({'Ticker':'count','Variation(%)':['mean','min','max']})
    .reset_index()
)
sector_stats.columns = ['Secteur','Nombre','Performance Moyenne (%)','Performance Min (%)','Performance Max (%)']
sector_stats.index += 1

sector_html = (
    sector_stats.style
      .format({
          'Performance Moyenne (%)':'{:+.2f}%',
          'Performance Min (%)':'{:+.2f}%',
          'Performance Max (%)':'{:+.2f}%'
      })
      .background_gradient(cmap='RdYlGn', subset=['Performance Moyenne (%)'], vmin=-50, vmax=150)
      .set_table_attributes('class="komorebi-table"')
      .to_html()
)
st.markdown(sector_html, unsafe_allow_html=True)

# --- Performances par pays ---
st.markdown("### Performances par pays")
country_stats = (
    analysis_df.groupby('Country')
    .agg({'Ticker':'count','Variation(%)':['mean','min','max']})
    .reset_index()
)
country_stats.columns = ['Pays','Nombre','Performance Moyenne (%)','Performance Min (%)','Performance Max (%)']
country_stats.index += 1

country_html = (
    country_stats.style
      .format({
          'Performance Moyenne (%)':'{:+.2f}%',
          'Performance Min (%)':'{:+.2f}%',
          'Performance Max (%)':'{:+.2f}%'
      })
      .background_gradient(cmap='RdYlGn', subset=['Performance Moyenne (%)'], vmin=-50, vmax=150)
      .set_table_attributes('class="komorebi-table"')
      .to_html()
)
st.markdown(country_html, unsafe_allow_html=True)

# Footer
st.markdown(create_footer(), unsafe_allow_html=True)