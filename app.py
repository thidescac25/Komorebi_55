import streamlit as st
import pandas as pd
import datetime
import sys
import os

# Ajouter le dossier src au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Importer les modules personnalisés
from src.data_loader import load_portfolio_data, get_stock_data
from src.stock_utils import get_currency_mapping, get_dividend_yields
from src.ui_components import apply_custom_css, create_scrolling_ticker, create_title, determine_currency
from src.visualization import create_stock_chart

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Komorebi Investments 55",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Appliquer le CSS personnalisé
apply_custom_css()

# Titre principal
st.markdown(create_title("Komorebi Investments 55 stocks", "page 1/3"), unsafe_allow_html=True)

# Chargement des données
portfolio_df = load_portfolio_data()

# Récupérer les mappings
currency_mapping = get_currency_mapping()
dividend_yields = get_dividend_yields()

# Récupérer les données boursières pour toutes les actions
@st.cache_data(ttl=60)  # Cache pour 60 secondes
def get_all_stock_data(tickers):
    data = {}
    for ticker in tickers:
        data[ticker] = get_stock_data(ticker)
    return data

# Récupérer les données des actions
tickers = portfolio_df['Ticker'].tolist()
stock_data_dict = get_all_stock_data(tickers)

# Création du bandeau défilant
st.markdown(create_scrolling_ticker(portfolio_df, stock_data_dict, currency_mapping), unsafe_allow_html=True)

# Texte pour le sélecteur de société
st.markdown('<div class="select-label">Sélectionnez une société</div>', unsafe_allow_html=True)

# Liste déroulante pour sélectionner une société
companies = portfolio_df['Société'].tolist()
selected_company = st.selectbox("", companies, label_visibility="collapsed")

# Trouver les données de la société sélectionnée
company_data = portfolio_df[portfolio_df['Société'] == selected_company].iloc[0]
ticker = company_data['Ticker']
business_model = company_data['Business_models']

# Récupérer les données boursières et financières
stock_data = get_stock_data(ticker, detailed=True)

# Récupérer la devise pour la société sélectionnée
currency = determine_currency(ticker)

# Affichage des informations de la société
st.markdown(f'''
<div class="company-header">
    {selected_company}
</div>
<div class="sector-header">{stock_data["industry"]} - {stock_data["country"]}</div>
''', unsafe_allow_html=True)

# Business Model
st.markdown('<div class="section-container">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Business Model de la société</div>', unsafe_allow_html=True)
st.markdown(f'<div class="business-text">{business_model}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Titre "Indicateurs" avec séparateur
st.markdown('<div class="section-container" style="padding-top:0;">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Indicateurs</div>', unsafe_allow_html=True)

# Métriques financières
col1, col2, col3, col4, col5 = st.columns(5)

# Couleur beige clair uniforme pour toutes les métriques
beige_bg = "#f9f5f2"  # Beige clair

# Valorisation - PER
with col1:
    st.markdown(
        f"""
        <div style="background-color:{beige_bg}; padding:20px; border-radius:10px; text-align:center;">
            <div style="font-size:14px; color:#693112;margin-bottom:10px;">📈 Valorisation</div>
            <div style="font-size:28px; font-weight:bold;">{stock_data['pe_ratio']:.1f}</div>
            <div style="font-size:14px; color:#888;">PER</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Rendement - Dividende
with col2:
    st.markdown(
        f"""
        <div style="background-color:{beige_bg}; padding:20px; border-radius:10px; text-align:center;">
            <div style="font-size:14px; color:#693112;margin-bottom:10px;">💰 Rendement</div>
            <div style="font-size:28px; font-weight:bold;">{stock_data['dividend_yield']:.2f}%</div>
            <div style="font-size:14px; color:#888;">Dividende</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Performance - YTD
with col3:
    ytd_class = "#28a745" if stock_data['ytd_change'] >= 0 else "#dc3545"
    ytd_sign = "+" if stock_data['ytd_change'] >= 0 else ""
    st.markdown(
        f"""
        <div style="background-color:{beige_bg}; padding:20px; border-radius:10px; text-align:center;">
            <div style="font-size:14px; color:#693112;margin-bottom:10px;">📊 Performance</div>
            <div style="font-size:28px; font-weight:bold; color:{ytd_class};">{ytd_sign}{stock_data['ytd_change']:.2f}%</div>
            <div style="font-size:14px; color:#888;">YTD</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# BPA
with col4:
    st.markdown(
        f"""
        <div style="background-color:{beige_bg}; padding:20px; border-radius:10px; text-align:center;">
            <div style="font-size:14px; color:#693112;margin-bottom:10px;">💵 BPA</div>
            <div style="font-size:28px; font-weight:bold;">{currency}{stock_data['eps']:.2f}</div>
            <div style="font-size:14px; color:#888;">Par action</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Capitalisation
with col5:
    st.markdown(
        f"""
        <div style="background-color:{beige_bg}; padding:20px; border-radius:10px; text-align:center;">
            <div style="font-size:14px; color:#693112;margin-bottom:10px;">💼 Capitalisation</div>
            <div style="font-size:28px; font-weight:bold;">{currency}{stock_data['market_cap']:.2f}B</div>
            <div style="font-size:14px; color:#888;">Milliards</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown('</div>', unsafe_allow_html=True)

# Section Performance
st.markdown('<div class="section-container">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Performance sur 52 semaines</div>', unsafe_allow_html=True)

# Récupérer l'historique des prix
hist = stock_data['history']

# Créer le graphique si l'historique existe
if not hist.empty:
    # Récupérer les statistiques et le graphique
    fig, avg_price, max_price, min_price = create_stock_chart(hist, ticker, currency)
    
    # Afficher les statistiques principales
    stats_col1, stats_col2, stats_col3 = st.columns(3)
    with stats_col1:
        st.markdown(f'''
        <div style="text-align: center;">
            <div style="font-size: 14px; color: #666;">Prix Moyen</div>
            <div style="font-size: 24px; font-weight: bold;">{currency}{avg_price:.1f}</div>
        </div>
        ''', unsafe_allow_html=True)
        
    with stats_col2:
        st.markdown(f'''
        <div style="text-align: center;">
            <div style="font-size: 14px; color: #666;">Plus Haut</div>
            <div style="font-size: 24px; font-weight: bold;">{currency}{max_price:.1f}</div>
            <div style="font-size: 12px; color: #28a745;">↑ {max_price - avg_price:.1f}</div>
        </div>
        ''', unsafe_allow_html=True)
        
    with stats_col3:
        st.markdown(f'''
        <div style="text-align: center;">
            <div style="font-size: 14px; color: #666;">Plus Bas</div>
            <div style="font-size: 24px; font-weight: bold;">{currency}{min_price:.1f}</div>
            <div style="font-size: 12px; color: #dc3545;">↓ {avg_price - min_price:.1f}</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Options de période
    periods = ["1 mois", "6 mois", "1 an"]
    period_selection = st.radio("Période", periods, horizontal=True, index=2)
    
    # Créer un nouveau graphique basé sur la période sélectionnée
    fig_period, _, _, _ = create_stock_chart(hist, ticker, currency, period_selection)
    
    # Afficher le graphique
    st.markdown(f'<div style="margin-top: 20px;">Évolution du cours - {period_selection}</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_period, use_container_width=True)
    
else:
    st.warning("Données historiques non disponibles pour cette action.")

st.markdown('</div>', unsafe_allow_html=True)

# Pied de page avec informations pour la navigation
st.markdown("""
<div style="margin-top: 30px; text-align: center; color: #693112; font-weight: bold;">
    Consultez les autres pages de l'application pour analyser en détail votre portefeuille de 55 valeurs.
</div>
""", unsafe_allow_html=True)