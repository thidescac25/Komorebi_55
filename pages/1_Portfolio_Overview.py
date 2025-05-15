import streamlit as st
import pandas as pd
import sys
import os

# Ajouter le dossier src au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importer les modules personnalisés
from src.data_loader import load_portfolio_data, get_stock_data, load_sector_country_data
from src.stock_utils import get_currency_mapping
from src.ui_components import apply_custom_css, create_scrolling_ticker, create_title, create_footer
from src.visualization import create_bar_charts  # Remplacé create_pie_charts par create_bar_charts

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Komorebi 55 - Vue d'ensemble",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Appliquer le CSS personnalisé
apply_custom_css()

# Titre principal
st.markdown(create_title("Komorebi Investments 55 - Vue d'ensemble", "page 2/3"), unsafe_allow_html=True)

# Chargement des données
portfolio_df = load_portfolio_data()

# Récupérer les mappings
currency_mapping = get_currency_mapping()

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

# Vue d'ensemble du portefeuille
st.markdown('<div class="section-title">Vue d\'ensemble du portefeuille</div>', unsafe_allow_html=True)

# Charger les données secteur/pays
df_sc = load_sector_country_data(tickers)

# Allocation égale pour chaque action
df_sc["Weight"] = 1.0 / len(df_sc)

# Créer les graphiques à barres horizontales au lieu des camemberts
fig_sector, fig_geo = create_bar_charts(df_sc)

# Afficher les graphiques côte à côte
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.plotly_chart(fig_sector, use_container_width=True)

with col_chart2:
    st.plotly_chart(fig_geo, use_container_width=True)

# Afficher une prévisualisation du portefeuille
st.markdown('<div class="section-title">Composition du portefeuille</div>', unsafe_allow_html=True)

# Définir un dictionnaire de mapping pour les devises en fonction du pays/marché du ticker
def determine_currency(ticker):
    # Pour les tickers américains (pas de suffixe)
    if '.' not in ticker:
        return "$"
    # Pour les tickers français (.PA)
    elif ticker.endswith('.PA'):
        return "€"
    # Pour les tickers japonais (.T)
    elif ticker.endswith('.T'):
        return "¥"
    # Pour les tickers britanniques (.L)
    elif ticker.endswith('.L'):
        return "£"
    # Pour les tickers suisses (.SW)
    elif ticker.endswith('.SW'):
        return "CHF"
    # Pour les tickers allemands (.DE)
    elif ticker.endswith('.DE'):
        return "€"
    # Pour les tickers néerlandais (.AS)
    elif ticker.endswith('.AS'):
        return "€"
    # Par défaut
    else:
        return "$"

# Calculer quelques statistiques pour chaque action
stats_data = []
for idx, row in portfolio_df.iterrows():
    ticker = row['Ticker']
    stock_data = stock_data_dict.get(ticker, {})
    company_name = row['Société']
    
    current_price = stock_data.get('current_price', 0)
    percent_change = stock_data.get('percent_change', 0)
    
    # Obtenir des données détaillées pour cette action
    detailed_data = get_stock_data(ticker, detailed=True)
    
    # Déterminer la devise correcte pour ce ticker
    currency = determine_currency(ticker)
    
    stats_data.append({
        'Société': company_name,
        'Ticker': ticker,
        'Prix': current_price,
        'Variation (%)': percent_change,
        'Devise': currency,  # Utiliser la devise déterminée par notre fonction
        'Secteur': detailed_data.get('sector', 'Non disponible'),
        'Pays': detailed_data.get('country', 'Non disponible')
    })

# Créer un DataFrame avec les statistiques
stats_df = pd.DataFrame(stats_data)

# Ajout d'un index qui commence à 1 et non à 0
stats_df.index = range(1, len(stats_df) + 1)

# Afficher le tableau
st.dataframe(
    stats_df.style.format({
        'Prix': '{:.2f}',
        'Variation (%)': '{:+.2f}%'
    }).background_gradient(
        cmap='RdYlGn', 
        subset=['Variation (%)']
    ),
    use_container_width=True,
    height=400
)

# Afficher des statistiques agrégées
st.markdown('<div class="section-title">Statistiques du portefeuille</div>', unsafe_allow_html=True)

# Calculer quelques statistiques globales
num_companies = len(tickers)
pos_perf = sum(1 for data in stats_data if data['Variation (%)'] > 0)
neg_perf = sum(1 for data in stats_data if data['Variation (%)'] < 0)
neutral_perf = sum(1 for data in stats_data if data['Variation (%)'] == 0)

# Pourcentages
pos_percent = (pos_perf / num_companies) * 100
neg_percent = (neg_perf / num_companies) * 100
neutral_percent = (neutral_perf / num_companies) * 100

# Afficher les statistiques globales
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div style="background-color:#f9f5f2; padding:20px; border-radius:10px; text-align:center;">
            <div style="font-size:14px; color:#693112;margin-bottom:10px;">📈 Nombre de valeurs</div>
            <div style="font-size:28px; font-weight:bold;">{num_companies}</div>
            <div style="font-size:14px; color:#888;">actions</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div style="background-color:#f9f5f2; padding:20px; border-radius:10px; text-align:center;">
            <div style="font-size:14px; color:#693112;margin-bottom:10px;">💹 Performances positives</div>
            <div style="font-size:28px; font-weight:bold; color:#28a745;">{pos_perf} ({pos_percent:.1f}%)</div>
            <div style="font-size:14px; color:#888;">valeurs en hausse</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div style="background-color:#f9f5f2; padding:20px; border-radius:10px; text-align:center;">
            <div style="font-size:14px; color:#693112;margin-bottom:10px;">📉 Performances négatives</div>
            <div style="font-size:28px; font-weight:bold; color:#dc3545;">{neg_perf} ({neg_percent:.1f}%)</div>
            <div style="font-size:14px; color:#888;">valeurs en baisse</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div style="background-color:#f9f5f2; padding:20px; border-radius:10px; text-align:center;">
            <div style="font-size:14px; color:#693112;margin-bottom:10px;">⚖️ Performances neutres</div>
            <div style="font-size:28px; font-weight:bold; color:#6c757d;">{neutral_perf} ({neutral_percent:.1f}%)</div>
            <div style="font-size:14px; color:#888;">valeurs stables</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Ajouter un pied de page
st.markdown(create_footer(), unsafe_allow_html=True)