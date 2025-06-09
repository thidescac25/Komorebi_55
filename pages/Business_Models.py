# ---- Imports principaux ----
import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
import plotly.graph_objects as go
import feedparser
from datetime import datetime, timedelta
from urllib.parse import quote_plus

# ---- Imports depuis les modules locaux ----
# Ajouter src/ au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

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
    page_title="Komorebi Investments 55 – Business Models",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

apply_custom_css()

# CSS pour les boutons de navigation
st.markdown("""
<style>
    .stButton > button {
        background-color: #5D4037 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        font-size: 16px !important;
        padding: 12px 20px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
    }
    
    .stButton > button:hover {
        background-color: #4A2C20 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0px) !important;
    }
</style>
""", unsafe_allow_html=True)

# ─── Titre principal ─────────────────────────────────────────────────────────
st.markdown(create_title("Business Models - Komorebi Investments 55 <span style='font-size:0.6em;'>(page 1/2)</span>"), unsafe_allow_html=True)

# Navigation
col1, col2 = st.columns(2)
with col1:
    if st.button("📊 Business Models", use_container_width=True):
        st.switch_page("pages/Business_Models.py")
with col2:
    if st.button("📈 Performance du Portefeuille", use_container_width=True):
        st.switch_page("pages/Performance_du_Portefeuille.py")

st.markdown("---")

# ─── Chargement des données ───────────────────────────────────────────────────
portfolio_df = load_portfolio_data()
currency_mapping = get_currency_mapping()
dividend_yields = get_dividend_yields()

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
sector_map = dict(zip(df_sc["Ticker"], df_sc["Sector"]))
country_map = dict(zip(df_sc["Ticker"], df_sc["Country"]))

# ─── Bandeau défilant ─────────────────────────────────────────────────────────
st.markdown(
    create_scrolling_ticker(portfolio_df, stock_data_dict, currency_mapping),
    unsafe_allow_html=True
)

# ─── Ajout d'espace après le bandeau défilant ──────────────────────────────────
st.markdown('<div style="height:30px;"></div>', unsafe_allow_html=True)  # Ajout de 30px d'espace

# ─── Sélecteur de société ────────────────────────────────────────────────────
st.markdown('<div class="select-label">Sélectionnez une société</div>', unsafe_allow_html=True)
company = st.selectbox("", portfolio_df["Société"].tolist(), label_visibility="collapsed")

row = portfolio_df[portfolio_df["Société"] == company].iloc[0]
ticker = row["Ticker"]
stock_data = get_stock_data(ticker, detailed=True)
currency = determine_currency(ticker)

# ─── En-tête société ─────────────────────────────────────────────────────────
st.markdown(f"""
<div class="company-header">{company}</div>
<div class="sector-header">{stock_data['industry']} – {stock_data['country']}</div>
""", unsafe_allow_html=True)

# ─── Business Model ─────────────────────────────────────────────────────────
st.markdown('<div class="section-container" style="padding-top:10px;">', unsafe_allow_html=True)  # Réduit le padding en haut
st.markdown('<div class="section-title">Business Model de la société</div>', unsafe_allow_html=True)
st.markdown(f'<div class="business-text">{row["Business_models"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ─── Statistiques du jour ───────────────────────────────────────────────────
st.markdown('<div class="section-container" style="padding-top:0;">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Statistiques du jour</div>', unsafe_allow_html=True)

cols = st.columns(5)
metrics = [
    ("Valorisation", stock_data["pe_ratio"], "PER", False),
    ("Rendement", stock_data["dividend_yield"], "Dividende", True),
    ("Performance", stock_data["ytd_change"], "YTD", True),
    ("BPA", stock_data["eps"], "Par action", False),
    ("Capitalisation", stock_data["market_cap"], "Milliards", False),
]
beige = "#f9f5f2"

for col, (title, val, subtitle, is_pct) in zip(cols, metrics):
    color = "#28a745" if is_pct and val >= 0 else "#dc3545" if is_pct else "#102040"
    disp = f"{val:+.2f}%" if is_pct else f"{val:.2f}"
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
    sel, *_ = st.radio("Période", ["1 mois", "6 mois", "1 an"], horizontal=True, index=2)
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
        "Société": r["Société"],
        "Variation (%) du jour": sd.get("percent_change", 0),
        "Prix": sd.get("current_price", 0),
        "Devise": determine_currency(r["Ticker"]),
        "Secteur": sector_map.get(r["Ticker"], "N/A"),
        "Pays": country_map.get(r["Ticker"], "N/A"),
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
    columnwidth=[40, 200, 120, 80, 60, 150, 120],  
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
        fill_color='#693112',  
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
        font=dict(size=13, color='#102040', family="Arial"),  
        fill_color=[
            'white', 
            'white',
            bg_colors, 
            'white',
            'white', 
            'white', 
            'white'
        ],
        align=['center', 'left', 'center', 'center', 'center', 'center', 'center'],
        line_color='lightgrey',  
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

n = len(comp_df)
pos = sum(v > 0 for v in comp_df["Variation (%) du jour"])
neg = sum(v < 0 for v in comp_df["Variation (%) du jour"])
neu = n - pos - neg
pos_p = pos / n * 100
neg_p = neg / n * 100
neu_p = neu / n * 100

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

# ─── Actualités des sociétés ───────────────────────────────────────────────────
st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-title">Actualités boursières des sociétés du Portefeuille</div>', unsafe_allow_html=True)

st.markdown('<div class="select-label">Sélectionnez une société pour prendre connaissance de son actualité boursière</div>', unsafe_allow_html=True)
news_company = st.selectbox("", portfolio_df["Société"].tolist(), label_visibility="collapsed", key="news_company_selector")

news_row = portfolio_df[portfolio_df["Société"] == news_company].iloc[0]
news_ticker = news_row["Ticker"]

@st.cache_data(ttl=3600)
def get_company_news(company_name: str, ticker: str):
    is_french = any(suffix in ticker for suffix in ['.PA', '.PAR', '.PARIS'])
    is_japanese = any(suffix in ticker for suffix in ['.T', '.TYO', '.TOKYO', '.JP'])
    
    # Obtenir le secteur et pays de la société depuis les dictionnaires
    company_sector = sector_map.get(ticker, "")
    company_country = country_map.get(ticker, "")
    
    # Ticker sans suffixe pour les recherches
    ticker_clean = ticker.split('.')[0]
    
    # Requêtes Google News optimisées pour trouver au moins 3 articles
    google_news_queries = [
        f"{company_name} {ticker_clean} stock",
        f"{company_name} bourse financial news",
        f"{company_name} {company_sector} market"
    ]
    
    # Construire les flux de base
    base_feeds = [
        f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US",
        f"https://seekingalpha.com/api/sa/combined/{ticker}.xml",
        f"https://feeds.finviz.com/rss/news.ashx?v=1&s={ticker}"
    ]
    
    # Ajouter les requêtes Google News
    for query in google_news_queries:
        encoded_query = query.replace(" ", "+")
        base_feeds.append(f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en")
    
    rss_feeds = base_feeds.copy()
    
    # Ajouter des flux spécifiques selon le pays
    if is_french:
        french_queries = [
            f"{company_name} bourse CAC actualité",
            f"{company_name} finance {ticker_clean}"
        ]
        
        rss_feeds.extend([
            f"https://www.easybourse.com/bourse/services/flux-rss/societe/{ticker.lower()}.rss",
            f"https://www.abcbourse.com/rss/valeurs/{ticker.lower()}",
            f"https://www.abcbourse.com/rss/analyses/{ticker.lower()}",
            "https://www.tradingsat.com/rssbourse.xml"
        ])
        
        for query in french_queries:
            encoded_query = query.replace(" ", "+")
            rss_feeds.append(f"https://news.google.com/rss/search?q={encoded_query}&hl=fr-FR&gl=FR&ceid=FR:fr")
            
    elif is_japanese:
        japanese_queries = [
            f"{company_name} {ticker_clean} japan stock",
            f"{company_name} nikkei tokyo"
        ]
        
        rss_feeds.extend([
            "https://www.jpx.co.jp/english/news/rss/index.xml",
            "https://asia.nikkei.com/rss/feed/index"
        ])
        
        for query in japanese_queries:
            encoded_query = query.replace(" ", "+")
            rss_feeds.append(f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en")
    
    news_list = []
    cutoff_time = datetime.utcnow() - timedelta(hours=48)
    min_articles_needed = 3
    articles_found = 0
    
    # Parcourir les flux jusqu'à trouver suffisamment d'articles
    for feed_url in rss_feeds:
        if articles_found >= min_articles_needed:
            break
            
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:10]:  # Limiter à 10 articles par flux pour l'efficacité
                if articles_found >= min_articles_needed:
                    break
                    
                if hasattr(entry, 'title'):
                    title_lower = entry.title.lower()
                    
                    company_parts = company_name.lower().split()
                    ticker_parts = ticker.lower().split('.')
                    company_name_lower = company_name.lower()
                    ticker_lower = ticker.split('.')[0].lower()
                    
                    match_found = False
                    
                    # Logique de filtre adaptée selon la source
                    if "tradingsat" in feed_url:
                        match_found = company_name_lower in title_lower or ticker_lower in title_lower
                    elif ("jpx" in feed_url or "nikkei" in feed_url) and is_japanese:
                        if any(part in title_lower for part in company_parts if len(part) > 2):
                            match_found = True
                        elif "tokyo" in title_lower or "nikkei" in title_lower or "japan" in title_lower:
                            match_found = True
                    elif any(part in title_lower for part in company_parts if len(part) > 2):
                        match_found = True
                    elif any(part in title_lower for part in ticker_parts if len(part) > 1):
                        match_found = True
                    
                    if match_found:
                        try:
                            entry_time = None
                            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                                entry_time = datetime(*entry.published_parsed[:6])
                            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                                entry_time = datetime(*entry.updated_parsed[:6])
                            
                            if entry_time and entry_time >= cutoff_time:
                                source = "Source financière"
                                if hasattr(entry, 'source') and hasattr(entry.source, 'title'):
                                    source = entry.source.title
                                elif "easybourse" in feed_url:
                                    source = "EasyBourse"
                                elif "abcbourse" in feed_url:
                                    source = "ABCBourse"
                                elif "tradingsat" in feed_url:
                                    source = "TradingSat"
                                elif "jpx" in feed_url:
                                    source = "Japan Exchange Group"
                                elif "nikkei" in feed_url:
                                    source = "Nikkei Asia"
                                elif "google" in feed_url:
                                    source = "Google News"
                                
                                # Éviter les doublons
                                if not any(item['title'] == entry.title for item in news_list):
                                    news_list.append({
                                        'title': entry.title,
                                        'link': entry.link,
                                        'date': entry_time.strftime("%d/%m/%Y %H:%M"),
                                        'source': source
                                    })
                                    articles_found += 1
                        except (AttributeError, TypeError):
                            continue
        except Exception as e:
            if st.session_state.get('dev_mode', False):
                st.error(f"Erreur lors de la récupération du flux {feed_url}: {str(e)}")
            continue
    
    # Si aucun article trouvé, essayer une dernière requête générique
    if not news_list:
        try:
            generic_query = f"{company_name} financial news"
            encoded_query = generic_query.replace(" ", "+")
            feed_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
            
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:3]:  # Juste les 3 premiers
                if hasattr(entry, 'title'):
                    try:
                        entry_time = None
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            entry_time = datetime(*entry.published_parsed[:6])
                        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                            entry_time = datetime(*entry.updated_parsed[:6])
                        
                        if entry_time:  # Accepter n'importe quelle date ici
                            news_list.append({
                                'title': entry.title,
                                'link': entry.link,
                                'date': entry_time.strftime("%d/%m/%Y %H:%M"),
                                'source': "Google News"
                            })
                    except (AttributeError, TypeError):
                        continue
        except Exception:
            pass
    
    # Trier par date (plus récentes d'abord) et limiter à 10 résultats max
    return sorted(news_list, key=lambda x: x['date'], reverse=True)[:10]

st.markdown("""
<style>
.news-container {
    margin-top: 10px;
}
.news-item {
    padding: 12px 15px;
    margin-bottom: 8px;
    border-radius: 8px;
    background-color: #f9f5f2;
    border-left: 4px solid #693112;
}
.news-source {
    font-size: 12px;
    color: #666;
    margin-bottom: 5px;
}
.news-title {
    font-size: 16px;
    font-weight: 500;
    color: #102040;
}
.news-link {
    display: inline-block;
    margin-top: 10px;
    color: #693112;
    text-decoration: none;
    font-weight: 500;
}
.news-link:hover {
    text-decoration: underline;
}
</style>
""", unsafe_allow_html=True)

with st.spinner(f"Chargement des actualités pour {news_company}..."):
    news = get_company_news(news_company, news_ticker)

    if news:
        for item in news:
            with st.expander(item["title"]):
                st.markdown(f"**Source:** {item['source']}")
                st.markdown(f"**Date:** {item['date']}")
                st.markdown(f"<a href='{item['link']}' target='_blank' class='news-link'>Lire l'article</a>", unsafe_allow_html=True)
    else:
        st.info(f"Aucune actualité récente trouvée pour {news_company} ({news_ticker})")

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown(create_footer(), unsafe_allow_html=True)