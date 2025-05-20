import streamlit as st
import base64

def apply_custom_css():
    """Applique un CSS personnalisé à l'application Streamlit."""
    st.markdown("""
    <style>
        .stApp {
            background-color: #ffffff;
        }
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        h1 {
            margin-bottom: 0.5rem;
        }
        .company-header {
            font-size: 32px;
            font-weight: bold;
            margin-top: 20px;
            margin-bottom: 5px;
            color: #102040;
        }
        .sector-header {
            font-size: 20px;
            font-weight: 500;
            margin-bottom: 25px;
            color: #555;
        }
        .section-container {
            padding: 25px 0;
        }
        .section-title {
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 20px;
            color: #693112;
            border-bottom: 3px solid #693112;
            padding-bottom: 10px;
        }
        .business-text {
            font-size: 18px;
            line-height: 1.6;
            font-weight: bold;
            text-align: justify;
        }
        .select-label {
            font-weight: bold;
            text-decoration: underline;
            color: #693112;
            margin-bottom: 10px;
            font-size: 18px;
        }
        .stSelectbox > div > div {
            background-color: #f9f5f2;
            border-color: #c0a080;
        }
        .stSelectbox > div > div > div {
            color: #693112;
            font-weight: 700 !important;
            font-size: 18px !important;
        }
        .chart-container {
            height: 400px;
            margin-top: 20px;
            margin-bottom: 20px;
        }
        .metric-container {
            background-color: #f9f5f2;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            text-align: center;
        }
        .metric-title {
            font-size: 16px;
            color: #693112;
            margin-bottom: 5px;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
        }
        .metric-subtitle {
            font-size: 12px;
            color: #888;
        }
        .positive {
            color: #28a745;
        }
        .negative {
            color: #dc3545;
        }
        .neutral {
            color: #102040;
        }
        .stock-info-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
            margin: 10px 0 20px 0;
        }
        .stock-info-item {
            background-color: #f9f5f2;
            border-radius: 5px;
            padding: 8px 12px;
            border-left: 4px solid #693112;
            min-width: 180px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    </style>
    """, unsafe_allow_html=True)

def determine_currency(ticker):
    """
    Détermine la devise d'un titre en fonction de son suffixe ou du ticker spécifique.
    
    Args:
        ticker (str): Symbole du titre
        
    Returns:
        str: Symbole de devise
    """
    # Cas spécifiques pour certaines actions
    specific_tickers = {
        '005830.KS': '₩',  # Hyundai Mobis
        '005380.KS': '₩',  # Hyundai Motors
        'MQG.AX': 'A$',    # Macquarie Group
    }
    
    if ticker in specific_tickers:
        return specific_tickers[ticker]
    
    # Pour les tickers avec extensions spécifiques
    if ticker.endswith('.KS'):  # Actions coréennes
        return "₩"
    elif ticker.endswith('.AX'):  # Actions australiennes
        return "A$"
    elif ticker.endswith('.HK'):  # Actions de Hong Kong
        return "HK$"
    elif ticker.endswith('.SS') or ticker.endswith('.SZ'):  # Actions chinoises
        return "¥"
    elif ticker.endswith('.PA'):  # Actions françaises
        return "€"
    elif ticker.endswith('.T'):   # Actions japonaises
        return "¥"
    elif ticker.endswith('.L'):   # Actions britanniques
        return "£"
    elif ticker.endswith('.SW'):  # Actions suisses
        return "CHF "
    elif ticker.endswith('.DE') or ticker.endswith('.F'):  # Actions allemandes
        return "€"
    elif ticker.endswith('.AS'):  # Actions néerlandaises
        return "€"
    elif ticker.endswith('.MI'):  # Actions italiennes
        return "€"
    elif ticker.endswith('.MC'):  # Actions espagnoles
        return "€"
    elif ticker.endswith('.ST'):  # Actions suédoises
        return "kr"
    elif ticker.endswith('.CO'):  # Actions danoises
        return "kr"
    elif ticker.endswith('.OL'):  # Actions norvégiennes
        return "kr"
    # Actions américaines (sans suffixe ou avec .N, .O, etc.)
    elif '.' not in ticker or ticker.endswith('.N') or ticker.endswith('.O'):
        return "$"
    # Cas par défaut
    else:
        return "$"

def create_scrolling_ticker(portfolio_df, stock_data_dict, currency_mapping):
    """
    Crée un bandeau défilant HTML avec les prix et variations des actions.
    
    Args:
        portfolio_df (DataFrame): DataFrame avec les données du portefeuille
        stock_data_dict (dict): Dictionnaire avec les données boursières
        currency_mapping (dict): Mapping des devises par ticker (non utilisé)
        
    Returns:
        str: HTML du bandeau défilant
    """
    # Générer le contenu HTML pour le bandeau défilant
    ticker_items = ""
    
    for _, row in portfolio_df.iterrows():
        ticker = row['Ticker']
        stock_data = stock_data_dict.get(ticker, {})
        
        # Déterminer la devise correcte en fonction du suffixe du ticker
        currency = determine_currency(ticker)
        
        # Valeurs par défaut si les données ne sont pas disponibles
        current_price = stock_data.get('current_price', 0)
        percent_change = stock_data.get('percent_change', 0)
        
        # Déterminer la classe CSS et flèche en fonction de la variation
        if percent_change >= 0:
            change_class = "positive"
            arrow = '<span style="font-size: 22px;">&#x25B2;</span>'
        else:
            change_class = "negative"
            arrow = '<span style="font-size: 22px;">&#x25BC;</span>'
        
        # Ajouter les informations de cette action au bandeau
        ticker_items += f"""
        <div class="ticker-item">
            <span class="ticker-name">{row['Société']}</span>
            <span class="ticker-price">{currency}{current_price:.2f}</span>
            <span class="ticker-change {change_class}">{arrow} {percent_change:.2f}%</span>
        </div>
        """
    
    # Code HTML complet pour le bandeau défilant
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                margin: 0;
                padding: 0;
                overflow: hidden;
                background-color: #102040;
                font-family: Arial, sans-serif;
            }}
            .ticker-container {{
                width: 100%;
                overflow: hidden;
                white-space: nowrap;
                padding: 12px 0;
            }}
            .ticker-tape {{
                display: inline-block;
                animation: ticker-scroll 350s linear infinite;
                padding-left: 100%;
            }}
            .ticker-item {{
                display: inline-block;
                padding: 0 50px;
                color: white;
                font-size: 18px;
            }}
            .ticker-name {{
                font-weight: bold;
                margin-right: 15px;
            }}
            .ticker-price {{
                margin-right: 15px;
            }}
            .positive {{
                color: #00ff00;
                font-weight: bold;
            }}
            .negative {{
                color: #ff4d4d;
                font-weight: bold;
            }}
            @keyframes ticker-scroll {{
                0% {{ transform: translate3d(0, 0, 0); }}
                100% {{ transform: translate3d(-100%, 0, 0); }}
            }}
        </style>
    </head>
    <body>
        <div class="ticker-container">
            <div class="ticker-tape">
                {ticker_items}
                {ticker_items}
            </div>
        </div>
    </body>
    </html>
    """
    
    # Encodage en base64 pour l'iframe
    b64 = base64.b64encode(html_content.encode("utf-8")).decode("utf-8")
    
    # Injecter l'iframe avec le contenu HTML
    iframe_html = f'<iframe src="data:text/html;base64,{b64}" width="100%" height="52px" frameborder="0" scrolling="no"></iframe>'
    
    return iframe_html

def create_metric_card(title, value, subtitle=None, is_currency=False, currency="€", is_percentage=False, positive_color=True):
    """
    Crée une carte métrique stylisée.
    
    Args:
        title (str): Titre de la métrique
        value (float/str): Valeur de la métrique
        subtitle (str, optional): Sous-titre de la métrique
        is_currency (bool): Si True, formate comme devise
        currency (str): Symbole de la devise
        is_percentage (bool): Si True, formate comme pourcentage
        positive_color (bool): Si True, utilise la couleur positive/negative selon la valeur
        
    Returns:
        str: HTML de la carte métrique
    """
    # Convertir la valeur en nombre si c'est une chaîne
    numeric_value = value
    if isinstance(value, str):
        try:
            numeric_value = float(value.replace(',', '').replace(' ', ''))
        except (ValueError, TypeError):
            numeric_value = 0
    
    # Déterminer la classe CSS pour la couleur
    value_class = "neutral"
    if positive_color:
        if isinstance(numeric_value, (int, float)):
            value_class = "positive" if numeric_value >= 0 else "negative"
    
    # Gérer le signe pour les valeurs positives
    sign = ""
    if isinstance(numeric_value, (int, float)) and numeric_value > 0:
        if is_currency or is_percentage:
            sign = "+"
    
    # Formater la valeur
    if isinstance(value, (int, float)):
        formatted_value = value
        if is_currency:
            if currency in ["$", "€", "£"]:
                formatted_value = f"{sign}{currency}{abs(value):,.0f}".replace(',', ' ')
            else:
                formatted_value = f"{sign}{abs(value):,.0f} {currency}".replace(',', ' ')
        elif is_percentage:
            formatted_value = f"{sign}{value:.2f}%"
    else:
        formatted_value = value 
    
    # Créer le HTML
    html = f"""
    <div class="metric-container">
        <div class="metric-title">{title}</div>
        <div class="metric-value {value_class}">{formatted_value}</div>
    """
    
    if subtitle:
        html += f'<div class="metric-subtitle">{subtitle}</div>'
    
    html += "</div>"
    
    return html

def create_footer():
    """Crée un pied de page pour l'application."""
    footer_html = """
    <div style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #666;">
        <p>Komorebi Investments © 2025 - Analyse de Portefeuille</p>
        <p style="font-size: 12px; margin-top: 10px;">Les informations présentées ne constituent en aucun cas un conseil d'investissement, ni une sollicitation à acheter ou vendre des instruments financiers. L'investisseur est seul responsable de ses décisions d'investissement.</p>
    </div>
    """
    return footer_html

def create_title(title, subtitle=None):
    """
    Crée un titre stylisé pour l'application.
    
    Args:
        title (str): Titre principal
        subtitle (str, optional): Sous-titre
        
    Returns:
        str: HTML du titre
    """
    html = f'<h1 style="font-size: 32px; margin-bottom: 10px;">{title}'
    
    if subtitle:
        html += f' <span style="font-size: 18px;">({subtitle})</span>'
    
    html += '</h1>'
    return html